from __future__ import annotations

import argparse as ap
import shlex
import tomllib
from dataclasses import dataclass
from pathlib import Path

from mahkrab import constants as c
from mahkrab.tools import config, parser


@dataclass(frozen=True)
class ConfigKeySpec:
    dest: str
    key: str
    label: str
    valueType: str
    aliases: tuple[str, ...] = ()


CONFIG_KEY_SPECS = (
    ConfigKeySpec('configEntry', 'entry', 'entry', 'string'),
    ConfigKeySpec('configCwd', 'cwd', 'cwd', 'string'),
    ConfigKeySpec('configBuildDir', 'build_dir', 'build dir', 'string'),
    ConfigKeySpec('configOutput', 'output', 'output', 'string'),
    ConfigKeySpec('configPython', 'python', 'python', 'string', aliases=('python_cmd',)),
    ConfigKeySpec('configLang', 'lang', 'lang', 'string'),
    ConfigKeySpec('configTool', 'tool', 'tool', 'string'),
    ConfigKeySpec('configRunOnCompile', 'run_on_compile', 'run on compile', 'bool'),
    ConfigKeySpec('configClear', 'clear', 'clear', 'bool'),
    ConfigKeySpec('configCompileArgs', 'compile_args', 'compile args', 'list', aliases=('tool_args',)),
    ConfigKeySpec('configProgramArgs', 'program_args', 'program args', 'list'),
)
CONFIG_MISSING = object()


def printError(message: str) -> None:
    print(
        f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI] - {c.Colours.RED}Error:{c.Colours.ENDC} {message}\n"
    )


def printSummary(configPath: Path, configData: dict) -> None:
    print(f"{c.Colours.MAGENTA}[MAHKRAB-CLI]{c.Colours.ENDC} Config")
    print(f"  config: {configPath}")
    for spec in CONFIG_KEY_SPECS:
        value = normalizedConfigValue(configData, spec)
        print(f"  {spec.label}: {displayValue(value, spec.valueType)}")

    envData = configData.get('env', {})
    print(f"  env: {displayEnv(envData)}")
    if 'os' in configData:
        print(f"  os: {displayValue(configData.get('os'), 'string')}")
    print()


def printGetter(specs: list[ConfigKeySpec], configData: dict) -> int:
    if len(specs) == 1:
        spec = specs[0]
        value = normalizedConfigValue(configData, spec)
        if value is CONFIG_MISSING:
            printError(f"Config key '{spec.key}' is not set.")
            return 2

        print(
            f"{c.Colours.MAGENTA}[MAHKRAB-CLI] -{c.Colours.ENDC} "
            f"{c.Colours.CYAN}{spec.label}:{c.Colours.ENDC} {displayValue(value, spec.valueType)}"
        )
        return 0

    print(f"{c.Colours.MAGENTA}[MAHKRAB-CLI]{c.Colours.ENDC} Config values")
    for spec in specs:
        value = normalizedConfigValue(configData, spec)
        if value is CONFIG_MISSING:
            printError(f"Config key '{spec.key}' is not set.")
            return 2

        print(f"  {spec.label}: {displayValue(value, spec.valueType)}")

    print()
    return 0


def printSetterResult(configPath: Path, changes: list[tuple[str, object, str, object]]) -> None:
    print(f"{c.Colours.MAGENTA}[MAHKRAB-CLI]{c.Colours.ENDC} Config updated")
    print(f"  config: {configPath}")
    for label, oldValue, valueType, newValue in changes:
        print(
            f"  {label}: {displayValue(oldValue, valueType)} -> {displayValue(newValue, valueType)}"
        )
    print()


def normalizedConfigValue(configData: dict, spec: ConfigKeySpec) -> object:
    rawValue = configValue(configData, spec)
    if rawValue is CONFIG_MISSING:
        return CONFIG_MISSING

    return normalizedValue(rawValue, spec.valueType, spec.key)


def configValue(configData: dict, spec: ConfigKeySpec) -> object:
    for key in (spec.key, *spec.aliases):
        if key in configData:
            return configData[key]

    return CONFIG_MISSING


def normalizedValue(rawValue: object, valueType: str, key: str) -> object:
    if valueType == 'bool':
        if isinstance(rawValue, bool):
            return rawValue

        raise ValueError(f"Config key '{key}' must be a boolean.")

    if valueType == 'list':
        return config.toStringList(rawValue)

    if rawValue is None:
        return CONFIG_MISSING

    if isinstance(rawValue, (dict, list)):
        raise ValueError(f"Config key '{key}' must be a string-compatible value.")

    return str(rawValue)


def displayValue(value: object, valueType: str) -> str:
    if value is CONFIG_MISSING:
        return '-'

    if valueType == 'bool':
        return 'true' if bool(value) else 'false'

    if valueType == 'list':
        items = list(value) if isinstance(value, list) else config.toStringList(value)
        return shlex.join(items) if items else '-'

    return str(value)


def displayEnv(envData: object) -> str:
    if envData in ({}, None):
        return '-'

    if not isinstance(envData, dict):
        raise ValueError("Config key 'env' must be a table.")

    values = [f'{key}={envData[key]}' for key in sorted(envData)]
    return ', '.join(values) if values else '-'


def parsedSetterValue(spec: ConfigKeySpec, rawValue: object) -> object:
    if rawValue is parser.CONFIG_GETTER:
        raise ValueError('Getter sentinel cannot be written.')

    if spec.valueType == 'bool':
        return parsedBool(str(rawValue), spec.key)

    if spec.valueType == 'list':
        return shlex.split(str(rawValue))

    return str(rawValue)


def parsedBool(rawValue: str, key: str) -> bool:
    normalized = rawValue.strip().lower()
    if normalized in {'true', '1'}:
        return True

    if normalized in {'false', '0'}:
        return False

    raise ValueError(
        f"Invalid value for '{key}': {rawValue}. Use true, false, 1, or 0."
    )


def parsedEnvAssignments(values: list[str]) -> list[tuple[str, str]]:
    assignments: list[tuple[str, str]] = []
    for value in values:
        if '=' not in value:
            raise ValueError(
                f"Invalid --env value: {value}. Use the form KEY=VALUE."
            )

        key, envValue = value.split('=', 1)
        if not key:
            raise ValueError(
                f"Invalid --env value: {value}. Use the form KEY=VALUE."
            )

        assignments.append((key, envValue))

    return assignments


def getterSpecs(args: ap.Namespace) -> list[ConfigKeySpec]:
    return [
        spec
        for spec in CONFIG_KEY_SPECS
        if getattr(args, spec.dest, None) is parser.CONFIG_GETTER
    ]


def setterSpecs(args: ap.Namespace) -> list[tuple[ConfigKeySpec, object]]:
    updates: list[tuple[ConfigKeySpec, object]] = []
    for spec in CONFIG_KEY_SPECS:
        rawValue = getattr(args, spec.dest, None)
        if rawValue not in (None, parser.CONFIG_GETTER):
            updates.append((spec, rawValue))

    return updates


def resolvedConfigPath(args: ap.Namespace) -> Path | None:
    return config.resolvedConfig(getattr(args, 'config', None), Path.cwd())


def missingConfigMessage(args: ap.Namespace) -> str:
    requestedConfig = getattr(args, 'config', None)
    if requestedConfig:
        return f'Config file not found: {config.resolveConfigPath(requestedConfig)}. Create one with mk init.'

    return 'No config found. Create one with mk init.'


def loadExistingConfig(configPath: Path) -> dict:
    data = config.loadConfig(configPath)
    if not isinstance(data, dict):
        raise ValueError('Config file must parse to a table.')

    return data


def applySetters(
    configPath: Path,
    configData: dict,
    valueSetters: list[tuple[ConfigKeySpec, object]],
    envValues: list[str],
) -> int:
    changes: list[tuple[str, object, str, object]] = []

    for spec, rawValue in valueSetters:
        oldValue = normalizedConfigValue(configData, spec)
        newValue = parsedSetterValue(spec, rawValue)
        configData[spec.key] = newValue
        for alias in spec.aliases:
            configData.pop(alias, None)
        changes.append((spec.label, oldValue, spec.valueType, newValue))

    if envValues:
        envData = configData.get('env', {})
        if envData in (None, {}):
            envTable: dict[str, str] = {}
        elif isinstance(envData, dict):
            envTable = {str(key): str(value) for key, value in envData.items()}
        else:
            raise ValueError("Config key 'env' must be a table.")

        for key, value in parsedEnvAssignments(envValues):
            oldValue = envTable.get(key, CONFIG_MISSING)
            envTable[key] = value
            changes.append((f'env.{key}', oldValue, 'string', value))

        configData['env'] = envTable

    config.writeConfig(configPath, configData)
    printSetterResult(configPath, changes)
    return 0


def run(args: ap.Namespace) -> int:
    configPath = resolvedConfigPath(args)
    getters = getterSpecs(args)
    setters = setterSpecs(args)
    envValues = list(getattr(args, 'configEnv', []))
    hasSetters = bool(setters or envValues)

    if getters and hasSetters:
        printError('Cannot mix config getters and setters in the same command.')
        return 2

    if configPath is None:
        printError(missingConfigMessage(args))
        return 2

    try:
        configData = loadExistingConfig(configPath)
    except tomllib.TOMLDecodeError as error:
        printError(f'Invalid TOML in config file ({error}).')
        return 2
    except (TypeError, ValueError) as error:
        printError(str(error))
        return 2

    try:
        if getters:
            return printGetter(getters, configData)

        if hasSetters:
            return applySetters(configPath, configData, setters, envValues)

        printSummary(configPath, configData)
        return 0
    except ValueError as error:
        printError(str(error))
        return 2
    except Exception as error:
        printError(f'An unexpected error occured {error}.')
        return 1
