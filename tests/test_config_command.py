import tomllib
from pathlib import Path

from mahkrab import cli


def readConfig(path: Path) -> dict:
    with path.open('rb') as configFile:
        return tomllib.load(configFile)


def writeConfig(path: Path, contents: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(contents, encoding='utf-8')


def test_config_without_existing_config_returns_helpful_error(monkeypatch, tmp_path: Path, capsys) -> None:
    monkeypatch.chdir(tmp_path)

    assert cli.main(['config']) == 2

    output = capsys.readouterr().out
    assert 'No config found' in output
    assert 'mk init' in output


def test_config_missing_explicit_config_returns_resolved_path(
    monkeypatch, tmp_path: Path, capsys
) -> None:
    missingPath = tmp_path / 'missing.toml'
    monkeypatch.chdir(tmp_path)

    assert cli.main(['config', '--config', str(missingPath)]) == 2

    output = capsys.readouterr().out
    assert f'Config file not found: {missingPath}' in output
    assert 'mk init' in output


def test_config_summary_prints_resolved_path_and_values(
    monkeypatch, tmp_path: Path, capsys
) -> None:
    configPath = tmp_path / '.mkconfig' / 'mkconfig.toml'
    writeConfig(
        configPath,
        '\n'.join(
            [
                'entry = "src/main.py"',
                'cwd = "src"',
                'build_dir = "out"',
                'output = "out/app"',
                'python = "python3.12"',
                'lang = "python"',
                'tool = "python3.12"',
                'run_on_compile = true',
                'clear = false',
                'compile_args = ["-X", "utf8"]',
                'program_args = ["--name", "Ada"]',
                '',
                '[env]',
                'FOO = "bar"',
                '',
            ]
        ),
    )
    monkeypatch.chdir(tmp_path)

    assert cli.main(['config']) == 0

    output = capsys.readouterr().out
    assert '[MAHKRAB-CLI]' in output
    assert str(configPath.resolve()) in output
    assert 'entry: src/main.py' in output
    assert 'build dir: out' in output
    assert 'compile args: -X utf8' in output
    assert 'program args: --name Ada' in output
    assert 'env: FOO=bar' in output


def test_config_entry_getter_prints_current_value(
    monkeypatch, tmp_path: Path, capsys
) -> None:
    configPath = tmp_path / '.mkconfig' / 'mkconfig.toml'
    writeConfig(configPath, 'entry = "src/main.py"\n')
    monkeypatch.chdir(tmp_path)

    assert cli.main(['config', '--entry']) == 0

    output = capsys.readouterr().out
    assert '[MAHKRAB-CLI]' in output
    assert 'entry:' in output
    assert 'src/main.py' in output


def test_config_entry_setter_updates_file_and_following_reads(
    monkeypatch, tmp_path: Path, capsys
) -> None:
    configPath = tmp_path / '.mkconfig' / 'mkconfig.toml'
    writeConfig(configPath, 'entry = "src/old.py"\n')
    monkeypatch.chdir(tmp_path)

    assert cli.main(['config', '--entry', 'src/main.py']) == 0

    updateOutput = capsys.readouterr().out
    assert 'Config updated' in updateOutput
    assert 'entry: src/old.py -> src/main.py' in updateOutput
    assert readConfig(configPath)['entry'] == 'src/main.py'

    assert cli.main(['config', '--entry']) == 0
    getterOutput = capsys.readouterr().out
    assert 'src/main.py' in getterOutput


def test_config_boolean_getters_and_setters(
    monkeypatch, tmp_path: Path, capsys
) -> None:
    configPath = tmp_path / '.mkconfig' / 'mkconfig.toml'
    writeConfig(
        configPath,
        'run_on_compile = false\nclear = true\n',
    )
    monkeypatch.chdir(tmp_path)

    assert cli.main(['config', '--run-on-compile']) == 0
    assert 'false' in capsys.readouterr().out

    assert cli.main(['config', '--run-on-compile', 'true']) == 0
    assert cli.main(['config', '--clear']) == 0
    assert 'true' in capsys.readouterr().out

    assert cli.main(['config', '--clear', '0']) == 0

    data = readConfig(configPath)
    assert data['run_on_compile'] is True
    assert data['clear'] is False


def test_config_boolean_setter_rejects_invalid_value(
    monkeypatch, tmp_path: Path, capsys
) -> None:
    configPath = tmp_path / '.mkconfig' / 'mkconfig.toml'
    writeConfig(configPath, 'run_on_compile = false\n')
    monkeypatch.chdir(tmp_path)

    assert cli.main(['config', '--run-on-compile', 'sometimes']) == 2

    output = capsys.readouterr().out
    assert "Invalid value for 'run_on_compile'" in output
    assert readConfig(configPath)['run_on_compile'] is False


def test_config_getter_for_unset_key_returns_error(
    monkeypatch, tmp_path: Path, capsys
) -> None:
    configPath = tmp_path / '.mkconfig' / 'mkconfig.toml'
    writeConfig(configPath, 'entry = "src/main.py"\n')
    monkeypatch.chdir(tmp_path)

    assert cli.main(['config', '--output']) == 2

    output = capsys.readouterr().out
    assert "Config key 'output' is not set." in output


def test_config_list_setters_update_compile_and_program_args(
    monkeypatch, tmp_path: Path, capsys
) -> None:
    configPath = tmp_path / '.mkconfig' / 'mkconfig.toml'
    writeConfig(configPath, 'entry = "src/main.c"\n')
    monkeypatch.chdir(tmp_path)

    assert cli.main(['config', '--compile-args', '-O2 -Wall']) == 0
    assert cli.main(['config', '--program-args', '--name Ada']) == 0

    data = readConfig(configPath)
    assert data['compile_args'] == ['-O2', '-Wall']
    assert data['program_args'] == ['--name', 'Ada']

    assert cli.main(['config', '--compile-args']) == 0
    assert '-O2 -Wall' in capsys.readouterr().out


def test_config_env_setter_updates_env_table(
    monkeypatch, tmp_path: Path, capsys
) -> None:
    configPath = tmp_path / '.mkconfig' / 'mkconfig.toml'
    writeConfig(
        configPath,
        '\n'.join(
            [
                'entry = "src/main.py"',
                '',
                '[env]',
                'FOO = "old"',
                '',
            ]
        ),
    )
    monkeypatch.chdir(tmp_path)

    assert cli.main(['config', '--env', 'FOO=bar', '--env', 'HELLO=world']) == 0

    output = capsys.readouterr().out
    assert 'env.FOO: old -> bar' in output
    assert 'env.HELLO: - -> world' in output

    data = readConfig(configPath)
    assert data['env'] == {'FOO': 'bar', 'HELLO': 'world'}


def test_config_env_setter_rejects_invalid_values(
    monkeypatch, tmp_path: Path, capsys
) -> None:
    configPath = tmp_path / '.mkconfig' / 'mkconfig.toml'
    writeConfig(configPath, 'entry = "src/main.py"\n')
    monkeypatch.chdir(tmp_path)

    assert cli.main(['config', '--env', 'FOO']) == 2
    assert 'Invalid --env value: FOO' in capsys.readouterr().out
    assert 'env' not in readConfig(configPath)

    assert cli.main(['config', '--env', '=bar']) == 2
    assert 'Invalid --env value: =bar' in capsys.readouterr().out
    assert 'env' not in readConfig(configPath)


def test_config_uses_explicit_config_path_for_getters_and_setters(
    monkeypatch, tmp_path: Path, capsys
) -> None:
    discoveredPath = tmp_path / '.mkconfig' / 'mkconfig.toml'
    explicitPath = tmp_path / 'configs' / 'custom.toml'
    writeConfig(discoveredPath, 'entry = "src/discovered.py"\n')
    writeConfig(explicitPath, 'entry = "src/explicit.py"\n')
    monkeypatch.chdir(tmp_path)

    assert cli.main(['config', '--config', str(explicitPath), '--entry']) == 0
    output = capsys.readouterr().out
    assert 'src/explicit.py' in output
    assert 'src/discovered.py' not in output

    assert (
        cli.main(['config', '--config', str(explicitPath), '--entry', 'src/updated.py'])
        == 0
    )

    assert readConfig(explicitPath)['entry'] == 'src/updated.py'
    assert readConfig(discoveredPath)['entry'] == 'src/discovered.py'
