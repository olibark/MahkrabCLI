import pytest

from mahkrab.tools import parser


@pytest.mark.parametrize("flag", ["-o", "--output"])
def test_parses_output_flag(flag: str) -> None:
    args = parser.parse_args(["main.c", flag, "build/app"])

    assert args.targetfile == "main.c"
    assert args.output == "build/app"


def test_parses_build_dir_flag() -> None:
    args = parser.parse_args(["main.c", "--build-dir", "out"])

    assert args.buildDir == "out"


def test_parses_cwd_flag() -> None:
    args = parser.parse_args(["main.c", "--cwd", "examples"])

    assert args.cwd == "examples"


def test_parses_config_flag() -> None:
    args = parser.parse_args(["run", "--config", ".mkconfig.toml"])

    assert args.command == "run"
    assert args.config == ".mkconfig.toml"


def test_parses_python_flag() -> None:
    args = parser.parse_args(["script.py", "--python", "python3.12"])

    assert args.pythonCmd == "python3.12"


def test_parses_lang_flag() -> None:
    args = parser.parse_args(["README.md", "--lang", "python"])

    assert args.lang == "python"


def test_parses_tool_flag() -> None:
    args = parser.parse_args(["main.cpp", "--tool", "clang++"])

    assert args.tool == "clang++"


@pytest.mark.parametrize("flag", ["-r", "--run-on-compile"])
def test_parses_run_on_compile_flag(flag: str) -> None:
    args = parser.parse_args(["main.c", flag])

    assert args.runOnCompile is True


@pytest.mark.parametrize("flag", ["--clear", "-c"])
def test_parses_clear_flag(flag: str) -> None:
    args = parser.parse_args(["main.py", flag])

    assert args.clear is True


@pytest.mark.parametrize("flag", ["-ls", "--list"])
def test_parses_list_flag_with_default_level(flag: str) -> None:
    args = parser.parse_args([flag])

    assert args.list == 1


@pytest.mark.parametrize("flag", ["-ls", "--list"])
def test_parses_list_flag_with_explicit_level(flag: str) -> None:
    args = parser.parse_args([flag, "3"])

    assert args.list == 3


@pytest.mark.parametrize(
    "flag, field",
    [
        ("-og", "ogs"),
        ("--ogs", "ogs"),
        ("-t", "terry"),
        ("--terry", "terry"),
        ("-e", "explain"),
        ("--explain", "explain"),
    ],
)
def test_parses_boolean_flags(flag: str, field: str) -> None:
    args = parser.parse_args(["main.py", flag])

    assert getattr(args, field) is True


@pytest.mark.parametrize("flag", ["-h", "--help"])
def test_help_flags_exit_successfully(flag: str, capsys) -> None:
    with pytest.raises(SystemExit) as error:
        parser.parse_args([flag])

    assert error.value.code == 0
    output = capsys.readouterr().out.lower()
    assert "usage:" in output
    assert "build" in output


@pytest.mark.parametrize("flag", ["-v", "--version"])
def test_version_flags_exit_successfully(flag: str, capsys) -> None:
    with pytest.raises(SystemExit) as error:
        parser.parse_args([flag])

    assert error.value.code == 0
    assert "mahkrab " in capsys.readouterr().out


def test_parses_program_args_and_unknown_values() -> None:
    args = parser.parse_args(
        [
            "main.go",
            '--program-args="-trimpath"',
            '--program-args="--ldflags=-s -w"',
            "--",
            "--runtime",
            "fast",
        ]
    )

    assert args.programArgs == ["-trimpath", "--ldflags=-s -w", "--runtime", "fast"]


def test_run_command_sets_command_instead_of_targetfile() -> None:
    args = parser.parse_args(["run"])

    assert args.command == "run"
    assert args.targetfile is None


def test_build_command_sets_command_instead_of_targetfile() -> None:
    args = parser.parse_args(["build"])

    assert args.command == "build"
    assert args.targetfile is None


def test_file_target_sets_targetfile() -> None:
    args = parser.parse_args(["script.py"])

    assert args.command is None
    assert args.targetfile == "script.py"


def test_unknown_args_without_program_args_exit() -> None:
    with pytest.raises(SystemExit) as error:
        parser.parse_args(["main.py", "--wat"])

    assert error.value.code == 2
