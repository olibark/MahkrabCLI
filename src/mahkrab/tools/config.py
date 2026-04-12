from __future__ import annotations

import argparse as ap
import os
import shlex
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from mahkrab import constants as c


@dataclass
class Settings:
    command: str | None = None
    targetfile: str | None = None
    entry: str | None = None
    outputfile: str | None = None
    cwd: str = '.'
    lang: str | None = None
    tool: str | None = None
    pythonCmd: str = c.PYTHON_PATH
    runOnCompile: bool = False
    clear: bool = False
    explain: bool = False
    buildDir: str = 'build'
    env: dict[str, str] = field(default_factory=dict)
    programArgs: list[str] = field(default_factory=list)
    configPath: str | None = None


def toStringList(value: object) -> list[str]:
    if value is None:
        return []

    if isinstance(value, str):
        return shlex.split(value)

    if isinstance(value, list):
        return [str(item) for item in value]

    return [str(value)]


def findConfig(startDir: Path) -> Path | None:
    for dirPath in (startDir, *startDir.parents):
        candidates = (
            dirPath / '.mkconfig' / '.mkconfig.toml',
            dirPath / '.mkconfig.toml',
            dirPath / '.mkconfig',
        )

        for candidate in candidates:
            if candidate.is_file():
                return candidate.resolve()

    return None


def resolveConfigPath(configArg: str) -> Path:
    configPath = Path(configArg).expanduser()
    if not configPath.is_absolute():
        configPath = (Path.cwd() / configPath).resolve()

    if configPath.is_dir():
        configPath = configPath / '.mkconfig.toml'

    return configPath


def configRoot(configPath: Path | None) -> Path:
    if configPath is None:
        return Path.cwd()

    if configPath.parent.name == '.mkconfig':
        return configPath.parent.parent

    return configPath.parent


def resolvePath(pathValue: str, baseDir: Path) -> Path:
    path = Path(pathValue).expanduser()
    if path.is_absolute():
        return path

    return (baseDir / path).resolve()


def loadConfig(configPath: Path | None) -> dict:
    if configPath is None:
        return {}

    with configPath.open('rb') as configFile:
        data = tomllib.load(configFile)

    if not isinstance(data, dict):
        raise TypeError('Config file must parse to a table.')

    return data


def buildSettings(args: ap.Namespace) -> Settings:
    invocationDir = Path.cwd().resolve()
    requestedConfig = getattr(args, 'config', None)
    if requestedConfig:
        configPath = resolveConfigPath(requestedConfig)
        if not configPath.is_file():
            raise FileNotFoundError(f'Config file not found: {configPath}')
    else:
        configPath = findConfig(Path.cwd())

    configData = loadConfig(configPath)
    rootDir = configRoot(configPath)

    command = getattr(args, 'command', None)
    entry = configData.get('entry')
    explicitTargetfile = getattr(args, 'targetfile', None)
    targetfile = explicitTargetfile
    if command == 'run' and not explicitTargetfile:
        targetfile = entry

    resolvedTargetfile = None
    if targetfile:
        targetBaseDir = invocationDir if explicitTargetfile else rootDir
        resolvedTargetfile = str(resolvePath(str(targetfile), targetBaseDir))

    argsCwd = getattr(args, 'cwd', None)
    configCwd = configData.get('cwd')
    if argsCwd:
        cwdPath = resolvePath(str(argsCwd), invocationDir)
    elif configCwd:
        cwdPath = resolvePath(str(configCwd), rootDir)
    elif command == 'run' and configPath is not None:
        cwdPath = rootDir
    else:
        cwdPath = invocationDir

    buildDir = str(configData.get('build_dir', 'build'))
    outputfile = getattr(args, 'output', None) or configData.get('output')
    if outputfile is None and resolvedTargetfile:
        filename = Path(resolvedTargetfile).stem
        outputfile = str(Path(buildDir) / filename)

    pythonCmd = (
        getattr(args, 'pythonCmd', None)
        or configData.get('python')
        or configData.get('python_cmd')
        or c.PYTHON_PATH
    )

    runOnCompile = bool(
        getattr(args, 'runOnCompile', False)
        or configData.get('run_on_compile', False)
    )
    if command == 'run':
        runOnCompile = True

    envData = configData.get('env', {})
    env = {}
    if isinstance(envData, dict):
        env = {str(key): str(value) for key, value in envData.items()}

    programArgs = (
        toStringList(configData.get('program_args'))
        + list(getattr(args, 'programArgs', []))
    )

    settings = Settings(
        command=command,
        targetfile=resolvedTargetfile,
        entry=str(entry) if entry else None,
        outputfile=str(outputfile) if outputfile else None,
        cwd=str(cwdPath),
        lang=getattr(args, 'lang', None) or configData.get('lang'),
        tool=getattr(args, 'tool', None) or configData.get('tool'),
        pythonCmd=str(pythonCmd),
        runOnCompile=runOnCompile,
        clear=bool(getattr(args, 'clear', False) or configData.get('clear', False)),
        explain=bool(getattr(args, 'explain', False)),
        buildDir=buildDir,
        env=env,
        programArgs=programArgs,
        configPath=str(configPath) if configPath else None,
    )

    return settings


def prepareRuntime(settings: Settings) -> Settings:
    cwdPath = Path(settings.cwd).expanduser().resolve()
    if not cwdPath.is_dir():
        raise NotADirectoryError(f'Working directory not found: {cwdPath}')

    os.chdir(cwdPath)

    if settings.targetfile:
        buildPath = Path(settings.buildDir)
        if not buildPath.is_absolute():
            buildPath = cwdPath / buildPath

        buildPath.mkdir(parents=True, exist_ok=True)

    if settings.env:
        os.environ.update(settings.env)

    return settings
