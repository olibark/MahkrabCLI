from __future__ import annotations

import argparse as ap
import json
import math
import os
import shlex
import tempfile
import tomllib
from datetime import date, datetime, time
from dataclasses import dataclass, field
from pathlib import Path

from mahkrab import constants as c
from mahkrab.tools.targetos import detectHostOs, normalizeTargetOs


@dataclass
class Settings:
    command: str | None = None
    targetfile: str | None = None
    entry: str | None = None
    outputfile: str | None = None
    cwd: str = '.'
    lang: str | None = None
    targetOs: str | None = None
    tool: str | None = None
    pythonCmd: str = c.PYTHON_PATH
    runOnCompile: bool = False
    clear: bool = False
    explain: bool = False
    buildDir: str = 'build'
    env: dict[str, str] = field(default_factory=dict)
    compileArgs: list[str] = field(default_factory=list)
    programArgs: list[str] = field(default_factory=list)
    configPath: str | None = None
    sources: dict[str, str] = field(default_factory=dict)
    doctorQuiet: bool = False
    doctorVerbose: bool = False
    doctorJson: bool = False
    doctorAll: bool = False
    doctorLanguages: bool = False


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
            dirPath / '.mkconfig' / 'mkconfig.toml',
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
        if configPath.name == '.mkconfig':
            candidates = (
                configPath / 'mkconfig.toml',
                configPath / '.mkconfig.toml',
            )
        else:
            candidates = (
                configPath / '.mkconfig' / 'mkconfig.toml',
                configPath / '.mkconfig' / '.mkconfig.toml',
                configPath / '.mkconfig.toml',
                configPath / '.mkconfig',
            )

        for candidate in candidates:
            if candidate.is_file():
                return candidate.resolve()

        configPath = candidates[0]

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


def resolvedConfig(configArg: str | None, startDir: Path | None = None) -> Path | None:
    if configArg:
        configPath = resolveConfigPath(configArg)
        if configPath.is_file():
            return configPath.resolve()

        return None

    baseDir = (startDir or Path.cwd()).resolve()
    return findConfig(baseDir)


def tomlKey(key: str) -> str:
    if key.replace('-', '').replace('_', '').isalnum():
        return key

    return json.dumps(key)


def tomlValue(value: object) -> str:
    if isinstance(value, bool):
        return 'true' if value else 'false'

    if isinstance(value, str):
        return json.dumps(value)

    if isinstance(value, int):
        return str(value)

    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError('Cannot write non-finite float values to TOML.')

        return repr(value)

    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, date):
        return value.isoformat()

    if isinstance(value, time):
        return value.isoformat()

    if isinstance(value, list):
        return '[' + ', '.join(tomlValue(item) for item in value) + ']'

    raise ValueError(f'Unsupported config value type: {type(value).__name__}')


def preferredScalarKeys(tablePath: tuple[str, ...]) -> list[str]:
    if not tablePath:
        return [
            'entry',
            'cwd',
            'build_dir',
            'output',
            'python',
            'python_cmd',
            'lang',
            'os',
            'tool',
            'run_on_compile',
            'clear',
            'compile_args',
            'tool_args',
            'program_args',
            'doctor_quiet',
            'doctor_verbose',
        ]

    if tablePath == ('doctor',):
        return ['quiet', 'verbose']

    return []


def preferredTableKeys(tablePath: tuple[str, ...]) -> list[str]:
    if not tablePath:
        return ['doctor', 'env']

    return []


def orderedKeys(keys: list[str], preferred: list[str]) -> list[str]:
    return [key for key in preferred if key in keys] + sorted(
        key for key in keys if key not in preferred
    )


def appendTomlTable(lines: list[str], tablePath: tuple[str, ...], tableData: dict) -> None:
    scalarKeys = orderedKeys(
        [str(key) for key, value in tableData.items() if not isinstance(value, dict)],
        preferredScalarKeys(tablePath),
    )
    tableKeys = orderedKeys(
        [str(key) for key, value in tableData.items() if isinstance(value, dict)],
        preferredTableKeys(tablePath),
    )

    if tablePath:
        if lines:
            lines.append('')
        lines.append('[' + '.'.join(tomlKey(part) for part in tablePath) + ']')

    for key in scalarKeys:
        lines.append(f'{tomlKey(key)} = {tomlValue(tableData[key])}')

    for key in tableKeys:
        value = tableData[key]
        if not isinstance(value, dict):
            raise ValueError(f'Config table {key} must be a TOML table.')

        appendTomlTable(lines, (*tablePath, key), value)


def dumpConfig(configData: dict) -> str:
    if not isinstance(configData, dict):
        raise ValueError('Config file must parse to a table.')

    lines: list[str] = []
    appendTomlTable(lines, (), configData)
    return '\n'.join(lines).rstrip() + '\n'


def writeConfig(configPath: Path, configData: dict) -> None:
    configPath.parent.mkdir(parents=True, exist_ok=True)
    serialized = dumpConfig(configData)

    with tempfile.NamedTemporaryFile(
        'w',
        encoding='utf-8',
        dir=configPath.parent,
        prefix=f'{configPath.name}.',
        suffix='.tmp',
        delete=False,
    ) as tempFile:
        tempFile.write(serialized)
        tempPath = Path(tempFile.name)

    os.replace(tempPath, configPath)


def getDoctorConfigValue(configData: dict, key: str, default: bool = False) -> bool:
    doctorData = configData.get('doctor', {})
    if isinstance(doctorData, dict) and key in doctorData:
        return bool(doctorData[key])

    return bool(configData.get(f'doctor_{key}', default))


def resolvedTargetOs(args: ap.Namespace, configData: dict) -> tuple[str, str]:
    argsTargetOs = normalizeTargetOs(getattr(args, 'targetOs', None))
    if argsTargetOs:
        return argsTargetOs, 'CLI option --os'

    configTargetOsRaw = configData.get('os')
    if configTargetOsRaw is not None:
        configTargetOs = normalizeTargetOs(configTargetOsRaw)
        if configTargetOs is None:
            raise ValueError(f'Unsupported config os value: {configTargetOsRaw}')

        return configTargetOs, 'config file'

    return detectHostOs(), 'detected host OS'


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
    argsCwd = getattr(args, 'cwd', None)
    configCwd = configData.get('cwd')
    if argsCwd:
        cwdPath = resolvePath(str(argsCwd), invocationDir)
    elif configCwd:
        cwdPath = resolvePath(str(configCwd), rootDir)
    elif command in ('build', 'run') and configPath is not None:
        cwdPath = rootDir
    else:
        cwdPath = invocationDir

    entry = configData.get('entry')
    explicitTargetfile = getattr(args, 'targetfile', None)
    doctorTarget = getattr(args, 'doctorTarget', None) if command == 'doctor' else None
    targetfile = explicitTargetfile
    if doctorTarget:
        targetfile = doctorTarget
    elif command in ('build', 'run') and not explicitTargetfile:
        targetfile = entry
    elif command == 'doctor' and not explicitTargetfile:
        targetfile = entry

    resolvedTargetfile = None
    if targetfile:
        if (explicitTargetfile or doctorTarget) and argsCwd:
            targetBaseDir = cwdPath
        elif explicitTargetfile or doctorTarget:
            targetBaseDir = invocationDir
        else:
            targetBaseDir = rootDir
        resolvedTargetfile = str(resolvePath(str(targetfile), targetBaseDir))

    buildDir = str(getattr(args, 'buildDir', None) or configData.get('build_dir', 'build'))
    outputfile = getattr(args, 'output', None) or configData.get('output')
    if outputfile is None and resolvedTargetfile:
        filename = Path(resolvedTargetfile).stem
        outputfile = str(Path(buildDir) / filename)

    argsPythonCmd = getattr(args, 'pythonCmd', None)
    configPythonCmd = configData.get('python') or configData.get('python_cmd')
    pythonCmd = argsPythonCmd or configPythonCmd or c.PYTHON_PATH
    if argsPythonCmd:
        pythonSource = 'CLI option --python'
    elif configPythonCmd:
        pythonSource = 'config file'
    elif os.environ.get('MAHKRAB_PYTHON') == c.PYTHON_PATH:
        pythonSource = 'environment variable MAHKRAB_PYTHON'
    else:
        pythonSource = 'default'

    runOnCompile = bool(
        getattr(args, 'runOnCompile', False)
        or configData.get('run_on_compile', False)
    )
    if command == 'run':
        runOnCompile = True
    elif command == 'build':
        runOnCompile = False

    envData = configData.get('env', {})
    env = {}
    if isinstance(envData, dict):
        env = {str(key): str(value) for key, value in envData.items()}

    compileArgs = (
        toStringList(configData.get('compile_args'))
        + toStringList(configData.get('tool_args'))
        + list(getattr(args, 'compileArgs', []))
    )
    programArgs = (
        toStringList(configData.get('program_args'))
        + list(getattr(args, 'programArgs', []))
    )

    argsTool = getattr(args, 'tool', None)
    configTool = configData.get('tool')
    sources = {
        'pythonCmd': pythonSource,
    }
    if argsTool:
        sources['tool'] = 'CLI option --tool'
    elif configTool:
        sources['tool'] = 'config file'

    targetOs, targetOsSource = resolvedTargetOs(args, configData)
    sources['targetOs'] = targetOsSource

    argsDoctorQuiet = bool(getattr(args, 'doctorQuiet', False))
    argsDoctorVerbose = bool(getattr(args, 'doctorVerbose', False))
    configDoctorQuiet = getDoctorConfigValue(configData, 'quiet')
    configDoctorVerbose = getDoctorConfigValue(configData, 'verbose')
    if argsDoctorQuiet:
        doctorQuiet = True
        doctorVerbose = False
        sources['doctorMode'] = 'CLI option --quiet'
    elif argsDoctorVerbose:
        doctorQuiet = False
        doctorVerbose = True
        sources['doctorMode'] = 'CLI option --verbose'
    elif configDoctorQuiet:
        doctorQuiet = True
        doctorVerbose = False
        sources['doctorMode'] = 'config file'
    elif configDoctorVerbose:
        doctorQuiet = False
        doctorVerbose = True
        sources['doctorMode'] = 'config file'
    else:
        doctorQuiet = False
        doctorVerbose = False
        sources['doctorMode'] = 'default'

    settings = Settings(
        command=command,
        targetfile=resolvedTargetfile,
        entry=str(entry) if entry else None,
        outputfile=str(outputfile) if outputfile else None,
        cwd=str(cwdPath),
        lang=getattr(args, 'lang', None) or configData.get('lang'),
        targetOs=targetOs,
        tool=argsTool or configTool,
        pythonCmd=str(pythonCmd),
        runOnCompile=runOnCompile,
        clear=bool(getattr(args, 'clear', False) or configData.get('clear', False)),
        explain=bool(getattr(args, 'explain', False)),
        buildDir=buildDir,
        env=env,
        compileArgs=compileArgs,
        programArgs=programArgs,
        configPath=str(configPath) if configPath else None,
        sources=sources,
        doctorQuiet=doctorQuiet,
        doctorVerbose=doctorVerbose,
        doctorJson=bool(getattr(args, 'doctorJson', False)),
        doctorAll=bool(getattr(args, 'doctorAll', False)),
        doctorLanguages=bool(getattr(args, 'doctorLanguages', False)),
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
