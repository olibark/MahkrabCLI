from __future__ import annotations

import os
import re
import subprocess
from dataclasses import dataclass

from mahkrab.assets.asmTable import searchAssemblyIncludeTable, searchAssemblySymbolTable
from mahkrab.assets.headerTable import searchHeaderTable


CPP_INCLUDE_PATTERN = re.compile(r'^\s*#include\s+[<"]([^">]+)[">]')
ASM_INCLUDE_PATTERN = re.compile(r'^\s*(?:%include|\.include)\s+["<]([^">]+)[">]', re.IGNORECASE)
SYMBOL_DIRECTIVE_PATTERN = re.compile(r'^\s*(?:extern|global|\.extern|\.globl|\.global)\s+(.+)$', re.IGNORECASE)
CALL_PATTERN = re.compile(
    r'\b(?:call|callq|jmp)\s+'
    r'(?:(?:qword|dword)\s+ptr\s+|qword\s+|dword\s+|rel\s+|offset\s+|near\s+|short\s+)*'
    r'([A-Za-z_.$?@][\w.$@?]*)',
    re.IGNORECASE,
)


@dataclass(frozen=True)
class AssemblyDependencyResult:
    compile_flags: list[str]
    link_flags: list[str]
    link_mode: str


def extendUniqueFlags(flags: list[str], additions: list[str] | tuple[str, ...]) -> None:
    existing_flags = set(flags)
    for flag in additions:
        if flag and flag not in existing_flags:
            flags.append(flag)
            existing_flags.add(flag)


def normalizeSymbol(symbol: str) -> str | None:
    normalized_symbol = str(symbol).strip().lstrip('*')
    if not normalized_symbol:
        return None

    if normalized_symbol.lower().startswith('rel '):
        normalized_symbol = normalized_symbol[4:].strip()
    if normalized_symbol.lower().startswith('offset '):
        normalized_symbol = normalized_symbol[7:].strip()

    normalized_symbol = normalized_symbol.split(':', 1)[0]
    normalized_symbol = normalized_symbol.split('@', 1)[0]
    normalized_symbol = normalized_symbol.strip('[](),')
    if not normalized_symbol:
        return None

    return normalized_symbol


def stripAssemblyComment(line: str) -> str:
    stripped_line = line
    if not stripped_line.lstrip().startswith('#include'):
        stripped_line = stripped_line.split('#', 1)[0]

    stripped_line = stripped_line.split(';', 1)[0]
    stripped_line = stripped_line.split('//', 1)[0]
    return stripped_line


def parseDirectiveSymbols(value: str) -> list[str]:
    symbols: list[str] = []
    for part in value.split(','):
        candidate = normalizeSymbol(part.split()[0]) if part.split() else None
        if candidate:
            symbols.append(candidate)

    return symbols


def scanAssemblySource(file_location: str) -> tuple[list[str], list[str]]:
    includes: list[str] = []
    symbols: list[str] = []

    with open(file_location, 'r', encoding='utf-8', errors='ignore') as file:
        for raw_line in file:
            line = stripAssemblyComment(raw_line).strip()
            if not line:
                continue

            include_match = CPP_INCLUDE_PATTERN.match(line) or ASM_INCLUDE_PATTERN.match(line)
            if include_match is not None:
                includes.append(include_match.group(1).strip())

            directive_match = SYMBOL_DIRECTIVE_PATTERN.match(line)
            if directive_match is not None:
                symbols.extend(parseDirectiveSymbols(directive_match.group(1)))

            for call_match in CALL_PATTERN.finditer(line):
                symbol = normalizeSymbol(call_match.group(1))
                if symbol:
                    symbols.append(symbol)

    return includes, symbols


def expandDependencyFlags(flags: list[str]) -> list[str]:
    expanded_flags: list[str] = []

    for flag in flags:
        if not flag.startswith('pkg-config '):
            expanded_flags.append(flag)
            continue

        try:
            result = subprocess.run(
                flag.split(),
                check=True,
                capture_output=True,
                text=True,
            )
        except (FileNotFoundError, subprocess.CalledProcessError):
            continue

        extendUniqueFlags(expanded_flags, result.stdout.split())

    return expanded_flags


def splitCompileAndLinkFlags(flags: list[str]) -> tuple[list[str], list[str]]:
    compile_flags: list[str] = []
    link_flags: list[str] = []

    index = 0
    while index < len(flags):
        flag = flags[index]

        if flag == '-pthread':
            extendUniqueFlags(compile_flags, [flag])
            extendUniqueFlags(link_flags, [flag])
        elif flag.startswith(('-I', '-D', '-U')):
            extendUniqueFlags(compile_flags, [flag])
        elif flag in {'-include', '-imacros', '-isystem', '-idirafter', '-iquote'} and index + 1 < len(flags):
            extendUniqueFlags(compile_flags, [flag, flags[index + 1]])
            index += 1
        else:
            extendUniqueFlags(link_flags, [flag])

        index += 1

    return compile_flags, link_flags


def applyHeaderDependency(include_name: str, compile_flags: list[str], link_flags: list[str]) -> bool:
    header_flags = searchHeaderTable(include_name, [])
    if not header_flags:
        return False

    expanded_flags = expandDependencyFlags(header_flags)
    header_compile_flags, header_link_flags = splitCompileAndLinkFlags(expanded_flags)
    extendUniqueFlags(compile_flags, header_compile_flags)
    extendUniqueFlags(link_flags, header_link_flags)
    return bool(header_compile_flags or header_link_flags)


def applyAssemblyDependency(
        include_or_symbol: str,
        compile_flags: list[str],
        link_flags: list[str],
        *,
        include_lookup: bool,
    ) -> tuple[bool, bool]:
    entry = (
        searchAssemblyIncludeTable(include_or_symbol)
        if include_lookup
        else searchAssemblySymbolTable(include_or_symbol)
    )
    if entry is None:
        return False, False

    extendUniqueFlags(compile_flags, entry.compile_flags)
    extendUniqueFlags(link_flags, entry.link_flags)
    if entry.add_no_pie:
        extendUniqueFlags(link_flags, ['-no-pie'])

    return entry.prefer_compiler_linker, True


def findDependencies(file_location: str) -> AssemblyDependencyResult:
    compile_flags: list[str] = []
    link_flags: list[str] = []
    prefer_compiler_linker = False

    try:
        includes, symbols = scanAssemblySource(file_location)
    except FileNotFoundError:
        return AssemblyDependencyResult([], [], 'ld')

    supports_cpp_style_includes = os.path.splitext(file_location)[1] == '.S'

    for include_name in includes:
        if supports_cpp_style_includes and applyHeaderDependency(include_name, compile_flags, link_flags):
            prefer_compiler_linker = True
            continue

        uses_compiler_linker, matched = applyAssemblyDependency(
            include_name,
            compile_flags,
            link_flags,
            include_lookup=True,
        )
        if matched and uses_compiler_linker:
            prefer_compiler_linker = True

    for symbol_name in symbols:
        uses_compiler_linker, matched = applyAssemblyDependency(
            symbol_name,
            compile_flags,
            link_flags,
            include_lookup=False,
        )
        if matched and uses_compiler_linker:
            prefer_compiler_linker = True

    link_mode = 'gcc' if prefer_compiler_linker or link_flags else 'ld'
    return AssemblyDependencyResult(compile_flags, link_flags, link_mode)
