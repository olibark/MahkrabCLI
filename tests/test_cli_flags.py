from types import SimpleNamespace

from mahkrab import cli


def make_args(**overrides):
    defaults = {
        "command": None,
        "list": None,
        "ogs": False,
        "terry": False,
    }
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


def make_settings(**overrides):
    defaults = {
        "targetfile": None,
        "outputfile": "build/out",
        "runOnCompile": False,
        "clear": False,
    }
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


def test_cli_runs_targetfile(monkeypatch) -> None:
    args = make_args()
    settings = make_settings(targetfile="/tmp/main.py", outputfile="build/main", runOnCompile=True)
    called = {}

    monkeypatch.setattr(cli.parser, "parse_args", lambda argv: args)
    monkeypatch.setattr(cli.config, "buildSettings", lambda parsed: settings)
    monkeypatch.setattr(cli.config, "prepareRuntime", lambda built: built)
    monkeypatch.setattr(
        cli.workflow,
        "run",
        lambda targetfile, outputfile, runtime_settings, run_on_compile: called.update(
            {
                "targetfile": targetfile,
                "outputfile": outputfile,
                "settings": runtime_settings,
                "runOnCompile": run_on_compile,
            }
        ),
    )

    assert cli.main(["main.py"]) == 0
    assert called == {
        "targetfile": "/tmp/main.py",
        "outputfile": "build/main",
        "settings": settings,
        "runOnCompile": True,
    }


def test_cli_builds_targetfile_and_returns_build_code(monkeypatch) -> None:
    args = make_args(command="build")
    settings = make_settings(targetfile="/tmp/main.c", outputfile="build/main", runOnCompile=False)
    called = {}

    monkeypatch.setattr(cli.parser, "parse_args", lambda argv: args)
    monkeypatch.setattr(cli.config, "buildSettings", lambda parsed: settings)
    monkeypatch.setattr(cli.config, "prepareRuntime", lambda built: built)
    monkeypatch.setattr(
        cli.workflow,
        "build",
        lambda targetfile, outputfile, runtime_settings: called.update(
            {
                "targetfile": targetfile,
                "outputfile": outputfile,
                "settings": runtime_settings,
            }
        )
        or 7,
    )

    assert cli.main(["build"]) == 7
    assert called == {
        "targetfile": "/tmp/main.c",
        "outputfile": "build/main",
        "settings": settings,
    }


def test_cli_runs_list_flag(monkeypatch) -> None:
    args = make_args(list=2)
    settings = make_settings()
    called = {}

    monkeypatch.setattr(cli.parser, "parse_args", lambda argv: args)
    monkeypatch.setattr(cli.config, "buildSettings", lambda parsed: settings)
    monkeypatch.setattr(cli.config, "prepareRuntime", lambda built: built)
    monkeypatch.setattr(cli.tree, "list", lambda level: called.setdefault("level", level))

    assert cli.main(["--list", "2"]) == 0
    assert called["level"] == 2


def test_cli_runs_ogs_flag(monkeypatch) -> None:
    args = make_args(ogs=True)
    settings = make_settings()
    called = {"ogs": 0}

    monkeypatch.setattr(cli.parser, "parse_args", lambda argv: args)
    monkeypatch.setattr(cli.config, "buildSettings", lambda parsed: settings)
    monkeypatch.setattr(cli.config, "prepareRuntime", lambda built: built)
    monkeypatch.setattr(cli.og, "ogs", lambda: called.__setitem__("ogs", called["ogs"] + 1))

    assert cli.main(["--ogs"]) == 0
    assert called["ogs"] == 1


def test_cli_runs_terry_flag(monkeypatch) -> None:
    args = make_args(terry=True)
    settings = make_settings()
    called = {"terry": 0}

    monkeypatch.setattr(cli.parser, "parse_args", lambda argv: args)
    monkeypatch.setattr(cli.config, "buildSettings", lambda parsed: settings)
    monkeypatch.setattr(cli.config, "prepareRuntime", lambda built: built)
    monkeypatch.setattr(cli.terry, "terry", lambda: called.__setitem__("terry", called["terry"] + 1))

    assert cli.main(["--terry"]) == 0
    assert called["terry"] == 1


def test_cli_runs_doctor_command(monkeypatch) -> None:
    args = make_args(command="doctor")
    settings = make_settings()
    called = {}

    monkeypatch.setattr(cli.parser, "parse_args", lambda argv: args)
    monkeypatch.setattr(cli.config, "buildSettings", lambda parsed: settings)
    monkeypatch.setattr(cli.config, "prepareRuntime", lambda built: built)

    def run_doctor(runtime_settings):
        called["settings"] = runtime_settings
        return 5

    monkeypatch.setattr(cli.doctor, "run", run_doctor)

    assert cli.main(["doctor"]) == 5
    assert called["settings"] is settings


def test_cli_clears_before_action(monkeypatch) -> None:
    args = make_args(ogs=True)
    settings = make_settings(clear=True)
    calls = []

    monkeypatch.setattr(cli.parser, "parse_args", lambda argv: args)
    monkeypatch.setattr(cli.config, "buildSettings", lambda parsed: settings)
    monkeypatch.setattr(cli.config, "prepareRuntime", lambda built: built)
    monkeypatch.setattr(cli.os, "system", lambda command: calls.append(command))
    monkeypatch.setattr(cli.og, "ogs", lambda: calls.append("ogs"))

    assert cli.main(["--clear", "--ogs"]) == 0
    assert calls == [cli.c.CLEAR, "ogs"]


def test_cli_clear_only_returns_success(monkeypatch) -> None:
    args = make_args()
    settings = make_settings(clear=True)
    calls = []

    monkeypatch.setattr(cli.parser, "parse_args", lambda argv: args)
    monkeypatch.setattr(cli.config, "buildSettings", lambda parsed: settings)
    monkeypatch.setattr(cli.config, "prepareRuntime", lambda built: built)
    monkeypatch.setattr(cli.os, "system", lambda command: calls.append(command))

    assert cli.main(["--clear"]) == 0
    assert calls == [cli.c.CLEAR]


def test_cli_run_command_without_entry_returns_error(monkeypatch, capsys) -> None:
    args = make_args(command="run")
    settings = make_settings(targetfile=None)

    monkeypatch.setattr(cli.parser, "parse_args", lambda argv: args)
    monkeypatch.setattr(cli.config, "buildSettings", lambda parsed: settings)
    monkeypatch.setattr(cli.config, "prepareRuntime", lambda built: built)

    assert cli.main(["run"]) == 2
    assert "No 'entry' configured" in capsys.readouterr().out


def test_cli_build_command_without_entry_returns_error(monkeypatch, capsys) -> None:
    args = make_args(command="build")
    settings = make_settings(targetfile=None)

    monkeypatch.setattr(cli.parser, "parse_args", lambda argv: args)
    monkeypatch.setattr(cli.config, "buildSettings", lambda parsed: settings)
    monkeypatch.setattr(cli.config, "prepareRuntime", lambda built: built)

    assert cli.main(["build"]) == 2
    assert "No 'entry' configured" in capsys.readouterr().out


def test_cli_reports_no_input_when_no_flags_or_target(monkeypatch, capsys) -> None:
    args = make_args()
    settings = make_settings()

    monkeypatch.setattr(cli.parser, "parse_args", lambda argv: args)
    monkeypatch.setattr(cli.config, "buildSettings", lambda parsed: settings)
    monkeypatch.setattr(cli.config, "prepareRuntime", lambda built: built)

    assert cli.main([]) == 2
    assert "No input file." in capsys.readouterr().out


def test_cli_returns_error_for_missing_config(monkeypatch, capsys) -> None:
    args = make_args(command="run")

    monkeypatch.setattr(cli.parser, "parse_args", lambda argv: args)
    monkeypatch.setattr(
        cli.config,
        "buildSettings",
        lambda parsed: (_ for _ in ()).throw(FileNotFoundError("Config file not found: /tmp/.mkconfig.toml")),
    )

    assert cli.main(["run", "--config", "/tmp/.mkconfig.toml"]) == 2
    assert "Config file not found" in capsys.readouterr().out
