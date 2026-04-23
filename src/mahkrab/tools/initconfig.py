from __future__ import annotations

import argparse as ap
import json
from pathlib import Path

from mahkrab import constants as c
from mahkrab.func import languages
from mahkrab.tools import config

CONFIG_DIR = '.mkconfig'
CONFIG_FILE = 'mkconfig.toml'


def printError(message: str) -> None:
    print(
        f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI] - {c.Colours.RED}Error:{c.Colours.ENDC} {message}\n"
    )


def printCreated(configPath: Path) -> None:
    print(
        f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI] -{c.Colours.ENDC} "
        f"Created {c.Colours.GREEN}{configPath}{c.Colours.ENDC}\n"
    )


def configPath(projectDir: Path) -> Path:
    return projectDir / CONFIG_DIR / CONFIG_FILE


def tomlString(value: str) -> str:
    return json.dumps(str(value))


def tomlBool(value: bool) -> str:
    return 'true' if value else 'false'


def relativePath(path: Path, projectDir: Path) -> str:
    return path.relative_to(projectDir).as_posix()


def commonEntryCandidates(projectDir: Path) -> tuple[Path, ...]:
    names = ('main', 'app', 'index')
    extensions = (
        '.py',
        '.c',
        '.cpp',
        '.js',
        '.ts',
        '.java',
        '.cs',
        '.go',
        '.rs',
        '.rb',
        '.sh',
    )

    return tuple(
        projectDir / directory / f'{name}{extension}'
        for directory in ('src', '.')
        for name in names
        for extension in extensions
    )


def inferEntry(projectDir: Path) -> str | None:
    for candidate in commonEntryCandidates(projectDir):
        if candidate.is_file():
            return relativePath(candidate, projectDir)

    supportedExtensions = {
        extension
        for extension in languages.EXTENSION_LANGUAGE_MAP
        if extension not in ('', '.exe')
    }
    directFiles = [
        path
        for path in projectDir.iterdir()
        if path.is_file() and path.suffix.lower() in supportedExtensions
    ]

    sourceDir = projectDir / 'src'
    sourceFiles: list[Path] = []
    if sourceDir.is_dir():
        sourceFiles = [
            path
            for path in sourceDir.iterdir()
            if path.is_file() and path.suffix.lower() in supportedExtensions
        ]

    candidates = sorted(sourceFiles + directFiles)
    if len(candidates) == 1:
        return relativePath(candidates[0], projectDir)

    return None


def selectedEntry(args: ap.Namespace, projectDir: Path) -> str | None:
    entry = getattr(args, 'initEntry', None) or getattr(args, 'initTarget', None)
    if entry:
        return str(entry)

    return inferEntry(projectDir)


def buildConfigContents(args: ap.Namespace, projectDir: Path) -> str:
    entry = selectedEntry(args, projectDir)
    lines = [
        '# Mahkrab project config',
        '# Used by mk run and mk build.',
        '',
    ]

    if entry:
        lines.append(f'entry = {tomlString(entry)}')
    else:
        lines.append('# entry = "src/main.py"')

    lang = getattr(args, 'lang', None)
    if lang:
        lines.append(f'lang = {tomlString(str(lang))}')

    lines.append(f'build_dir = {tomlString(str(getattr(args, "buildDir", None) or "build"))}')

    output = getattr(args, 'output', None)
    if output:
        lines.append(f'output = {tomlString(str(output))}')

    lines.append(f'run_on_compile = {tomlBool(bool(getattr(args, "runOnCompile", False)))}')
    lines.append('')

    return '\n'.join(lines)


def existingConfig(projectDir: Path) -> Path | None:
    return config.findConfig(projectDir)


def run(args: ap.Namespace) -> int:
    projectDir = Path.cwd().resolve()
    outputPath = configPath(projectDir)
    existingPath = existingConfig(projectDir)

    if existingPath is not None and not getattr(args, 'force', False):
        printError(f'Config already exists: {existingPath}')
        return 2

    if outputPath.parent.exists() and not outputPath.parent.is_dir():
        printError(f'Cannot create config directory because a file exists: {outputPath.parent}')
        return 2

    outputPath.parent.mkdir(parents=True, exist_ok=True)
    outputPath.write_text(buildConfigContents(args, projectDir), encoding='utf-8')
    printCreated(outputPath)
    return 0
