from pathlib import Path

import pytest

from mahkrab.func import run
from mahkrab.tools import config, parser


def test_parse_args_splits_compile_and_program_args() -> None:
    args = parser.parse_args(
        ['main.c', '-r', '--compile-args', '-O2', '--program-args', '--', 'hello', 'world']
    )

    assert args.compileArgs == ['-O2']
    assert args.programArgs == ['hello', 'world']


def test_parse_args_routes_bare_dash_dash_to_program_args() -> None:
    args = parser.parse_args(['main.c', '-r', '--', 'hello', 'world'])

    assert args.compileArgs == []
    assert args.programArgs == ['hello', 'world']


def test_parse_args_rejects_unknown_args_without_program_forwarding() -> None:
    with pytest.raises(SystemExit) as excinfo:
        parser.parse_args(['main.c', '-r', 'hello'])

    assert excinfo.value.code == 2


def test_build_settings_merges_compile_and_program_args(tmp_path: Path) -> None:
    config_path = tmp_path / '.mkconfig.toml'
    config_path.write_text(
        'entry = "src/main.py"\n'
        'compile_args = ["-X", "utf8"]\n'
        'program_args = ["cfg-arg"]\n'
        'tool_args = ["-B"]\n',
        encoding='utf-8',
    )

    args = parser.parse_args(
        [
            'run',
            '--config',
            str(config_path),
            '--compile-args',
            '-W',
            '--program-args',
            '--',
            'cli-arg',
        ]
    )
    settings = config.buildSettings(args)

    assert settings.compileArgs == ['-X', 'utf8', '-B', '-W']
    assert settings.programArgs == ['cfg-arg', 'cli-arg']
    assert settings.targetfile == str((tmp_path / 'src/main.py').resolve())


@pytest.mark.parametrize(
    ('argv', 'compile_arg', 'program_arg'),
    [
        (['main.c', '-r', '--compile-args', '-O2', '--program-args', '--', 'hello'], '-O2', 'hello'),
        (['Main.java', '-r', '--compile-args', '-Xlint', '--program-args', '--', 'hello'], '-Xlint', 'hello'),
    ],
)
def test_compiled_plan_routes_args_to_correct_command(
    argv: list[str],
    compile_arg: str,
    program_arg: str,
) -> None:
    settings = config.buildSettings(parser.parse_args(argv))
    plan = run.build_execution_plan(settings.targetfile, settings.outputfile, settings, settings.runOnCompile)

    assert plan is not None
    assert compile_arg in plan['compile_cmd']
    assert program_arg not in plan['compile_cmd']
    assert plan['run_cmd'][-1] == program_arg


def test_python_plan_routes_interpreter_and_program_args() -> None:
    settings = config.buildSettings(
        parser.parse_args(['script.py', '--compile-args', '-X', 'utf8', '--program-args', '--', 'hello'])
    )
    plan = run.build_execution_plan(settings.targetfile, settings.outputfile, settings, settings.runOnCompile)

    assert plan is not None
    assert plan['run_cmd'][1:4] == ['-u', '-X', 'utf8']
    assert plan['run_cmd'][-2:] == [str(Path('script.py').resolve()), 'hello']
