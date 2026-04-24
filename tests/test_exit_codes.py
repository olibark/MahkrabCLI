import subprocess
from pathlib import Path
from types import SimpleNamespace

from mahkrab import cli
from mahkrab.func import workflow
from mahkrab.func.executors.compiled import binexec, cexec, cmdexec
from mahkrab.func.executors.interpreted import interpexec, pyexec, sqlexec
from mahkrab.tools import config, parser


def make_args(**overrides):
    defaults = {
        'compileArgs': [],
        'programArgs': [],
        'pythonCmd': 'python',
        'tool': None,
    }
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


def test_python_executor_returns_child_exit_code(monkeypatch, tmp_path: Path) -> None:
    script = tmp_path / 'fail.py'
    script.write_text('raise SystemExit(13)\n', encoding='utf-8')

    def fail_run(run_cmd: list[str]) -> None:
        raise subprocess.CalledProcessError(13, run_cmd)

    monkeypatch.setattr(pyexec.Executor, 'run', staticmethod(fail_run))

    assert pyexec.Executor.exec(str(script), '', make_args()) == 13


def test_python_executor_returns_127_for_missing_interpreter(monkeypatch, tmp_path: Path) -> None:
    script = tmp_path / 'ok.py'
    script.write_text('print("ok")\n', encoding='utf-8')

    def missing_run(run_cmd: list[str]) -> None:
        raise FileNotFoundError

    monkeypatch.setattr(pyexec.Executor, 'run', staticmethod(missing_run))

    assert pyexec.Executor.exec(str(script), '', make_args(pythonCmd='missing-python')) == 127


def test_generic_interpreted_executor_returns_status_codes(monkeypatch) -> None:
    def fail_run(run_cmd: list[str]) -> None:
        raise subprocess.CalledProcessError(26, run_cmd)

    monkeypatch.setattr(interpexec.Executor, 'run', staticmethod(fail_run))

    assert interpexec.Executor.exec(['node', 'script.js'], 'node', make_args()) == 26


def test_sql_executor_returns_status_codes(monkeypatch, tmp_path: Path) -> None:
    script = tmp_path / 'bad.sql'
    script.write_text('select nope;\n', encoding='utf-8')

    def fail_run(full_path: str, run_cmd: list[str]) -> None:
        raise subprocess.CalledProcessError(27, run_cmd)

    monkeypatch.setattr(sqlexec.Executor, 'run', staticmethod(fail_run))

    assert sqlexec.Executor.exec(str(script), '', make_args()) == 27


def test_compiled_executor_returns_run_on_compile_exit_code(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / 'main.c'
    source.write_text('int main(void) { return 23; }\n', encoding='utf-8')

    def fail_run_on_compile(cmd: list[str], run_cmd: list[str]) -> None:
        raise subprocess.CalledProcessError(23, run_cmd)

    monkeypatch.setattr(cexec.Executor, 'findFlags', staticmethod(lambda full_path: []))
    monkeypatch.setattr(cexec.Executor, 'runOnCompile', staticmethod(fail_run_on_compile))

    assert cexec.Executor.exec(str(source), str(tmp_path / 'main'), make_args(), True) == 23


def test_command_compiled_executor_returns_status_codes(monkeypatch) -> None:
    def fail_run_on_compile(cmd: list[str], run_cmd: list[str]) -> None:
        raise subprocess.CalledProcessError(24, run_cmd)

    monkeypatch.setattr(cmdexec.Executor, 'runOnCompile', staticmethod(fail_run_on_compile))

    assert cmdexec.Executor.exec(['compiler'], ['program'], 'compiler', True) == 24


def test_binary_executor_returns_status_codes(monkeypatch, tmp_path: Path) -> None:
    binary = tmp_path / 'program'
    binary.write_text('', encoding='utf-8')

    def fail_run(run_cmd: list[str]) -> None:
        raise subprocess.CalledProcessError(25, run_cmd)

    monkeypatch.setattr(binexec, 'run', fail_run)

    assert binexec.execbin(str(binary), 'build', []) == 25


def test_workflow_run_returns_2_for_unsupported_language(tmp_path: Path) -> None:
    target = tmp_path / 'program.unknown'
    target.write_text('', encoding='utf-8')
    settings = config.buildSettings(parser.parse_args([str(target)]))

    assert workflow.run(settings.targetfile, settings.outputfile, settings, settings.runOnCompile) == 2


def test_workflow_run_propagates_executor_exit_code(monkeypatch, tmp_path: Path) -> None:
    target = tmp_path / 'fail.py'
    target.write_text('raise SystemExit(17)\n', encoding='utf-8')
    settings = config.buildSettings(parser.parse_args([str(target)]))

    monkeypatch.setattr(pyexec.Executor, 'exec', staticmethod(lambda *args: 17))

    assert workflow.run(settings.targetfile, settings.outputfile, settings, settings.runOnCompile) == 17


def test_cli_targetfile_returns_workflow_run_exit_code(monkeypatch) -> None:
    args = SimpleNamespace(command=None, ogs=False, terry=False)
    settings = SimpleNamespace(
        targetfile='/tmp/fail.py',
        outputfile='build/fail',
        runOnCompile=True,
        clear=False,
    )

    monkeypatch.setattr(cli.parser, 'parse_args', lambda argv: args)
    monkeypatch.setattr(cli.config, 'buildSettings', lambda parsed: settings)
    monkeypatch.setattr(cli.config, 'prepareRuntime', lambda built: built)
    monkeypatch.setattr(cli.workflow, 'run', lambda *args: 18)

    assert cli.main(['fail.py']) == 18


def test_cli_run_command_returns_workflow_run_exit_code(monkeypatch) -> None:
    args = SimpleNamespace(command='run', ogs=False, terry=False)
    settings = SimpleNamespace(
        targetfile='/tmp/fail.py',
        outputfile='build/fail',
        runOnCompile=True,
        clear=False,
    )

    monkeypatch.setattr(cli.parser, 'parse_args', lambda argv: args)
    monkeypatch.setattr(cli.config, 'buildSettings', lambda parsed: settings)
    monkeypatch.setattr(cli.config, 'prepareRuntime', lambda built: built)
    monkeypatch.setattr(cli.workflow, 'run', lambda *args: 19)

    assert cli.main(['run']) == 19
