import tomllib
from pathlib import Path

from mahkrab import cli
from mahkrab.tools import config, parser
from mahkrab.tools import initconfig


def readConfig(path: Path) -> dict:
    with path.open('rb') as configFile:
        return tomllib.load(configFile)


def test_parse_init_command() -> None:
    args = parser.parse_args(['init'])

    assert args.command == 'init'
    assert args.initTarget is None
    assert args.targetfile is None


def test_parse_init_target() -> None:
    args = parser.parse_args(['init', 'main.py'])

    assert args.command == 'init'
    assert args.initTarget == 'main.py'
    assert args.targetfile is None


def test_parse_init_entry_option() -> None:
    args = parser.parse_args(['init', '--entry', 'src/main.py'])

    assert args.command == 'init'
    assert args.initEntry == 'src/main.py'
    assert args.targetfile is None


def test_init_creates_mkconfig_file(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)

    assert cli.main(['init', 'main.py']) == 0

    assert (tmp_path / '.mkconfig').is_dir()
    assert (tmp_path / '.mkconfig' / 'mkconfig.toml').is_file()


def test_init_generated_config_loads_for_run(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / 'main.py'
    source.write_text('print("ok")\n', encoding='utf-8')
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(initconfig, 'detectHostOs', lambda: 'linux')

    assert cli.main(['init', 'main.py']) == 0

    settings = config.buildSettings(parser.parse_args(['run']))
    assert settings.configPath == str((tmp_path / '.mkconfig' / 'mkconfig.toml').resolve())
    assert settings.targetfile == str(source.resolve())
    assert settings.targetOs == 'linux'


def test_config_discovery_finds_generated_path(tmp_path: Path) -> None:
    configDir = tmp_path / '.mkconfig'
    configDir.mkdir()
    generatedConfig = configDir / 'mkconfig.toml'
    generatedConfig.write_text('entry = "main.py"\n', encoding='utf-8')

    assert config.findConfig(tmp_path) == generatedConfig.resolve()


def test_init_refuses_to_overwrite_existing_config(monkeypatch, tmp_path: Path, capsys) -> None:
    configDir = tmp_path / '.mkconfig'
    configDir.mkdir()
    generatedConfig = configDir / 'mkconfig.toml'
    generatedConfig.write_text('entry = "old.py"\n', encoding='utf-8')
    monkeypatch.chdir(tmp_path)

    assert cli.main(['init', '--entry', 'new.py']) == 2

    assert readConfig(generatedConfig)['entry'] == 'old.py'
    assert 'Config already exists' in capsys.readouterr().out


def test_init_force_overwrites_existing_config(monkeypatch, tmp_path: Path) -> None:
    configDir = tmp_path / '.mkconfig'
    configDir.mkdir()
    generatedConfig = configDir / 'mkconfig.toml'
    generatedConfig.write_text('entry = "old.py"\n', encoding='utf-8')
    monkeypatch.chdir(tmp_path)

    assert cli.main(['init', '--force', '--entry', 'src/main.c']) == 0

    assert readConfig(generatedConfig)['entry'] == 'src/main.c'


def test_init_force_reports_legacy_file_conflict(monkeypatch, tmp_path: Path, capsys) -> None:
    legacyConfig = tmp_path / '.mkconfig'
    legacyConfig.write_text('entry = "old.py"\n', encoding='utf-8')
    monkeypatch.chdir(tmp_path)

    assert cli.main(['init', '--force', '--entry', 'new.py']) == 2

    assert legacyConfig.read_text(encoding='utf-8') == 'entry = "old.py"\n'
    assert 'Cannot create config directory' in capsys.readouterr().out


def test_init_writes_supported_runtime_keys(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(initconfig, 'detectHostOs', lambda: 'linux')

    assert cli.main(
        [
            'init',
            '--entry',
            'src/main.c',
            '--lang',
            'c',
            '--build-dir',
            'out',
            '--output',
            'out/app',
            '--run-on-compile',
        ]
    ) == 0

    data = readConfig(tmp_path / '.mkconfig' / 'mkconfig.toml')
    assert data['entry'] == 'src/main.c'
    assert data['lang'] == 'c'
    assert data['os'] == 'linux'
    assert data['build_dir'] == 'out'
    assert data['output'] == 'out/app'
    assert data['run_on_compile'] is True


def test_init_writes_explicit_target_os(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(initconfig, 'detectHostOs', lambda: 'linux')

    assert cli.main(['init', '--entry', 'src/main.py', '--os', 'windows']) == 0

    data = readConfig(tmp_path / '.mkconfig' / 'mkconfig.toml')
    assert data['os'] == 'windows'


def test_init_infers_common_entry(monkeypatch, tmp_path: Path) -> None:
    sourceDir = tmp_path / 'src'
    sourceDir.mkdir()
    (sourceDir / 'main.py').write_text('print("ok")\n', encoding='utf-8')
    monkeypatch.chdir(tmp_path)

    assert cli.main(['init']) == 0

    assert readConfig(tmp_path / '.mkconfig' / 'mkconfig.toml')['entry'] == 'src/main.py'


def test_existing_command_parsing_still_works() -> None:
    runArgs = parser.parse_args(['run'])
    buildArgs = parser.parse_args(['build'])
    directArgs = parser.parse_args(['main.py'])

    assert runArgs.command == 'run'
    assert runArgs.targetfile is None
    assert buildArgs.command == 'build'
    assert buildArgs.targetfile is None
    assert directArgs.command is None
    assert directArgs.targetfile == 'main.py'


def test_init_options_do_not_break_compile_arg_forwarding() -> None:
    args = parser.parse_args(['main.c', '--compile-args', '--force', '--entry', 'value'])

    assert args.command is None
    assert args.targetfile == 'main.c'
    assert args.compileArgs == ['--force', '--entry', 'value']
