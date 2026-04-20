from __future__ import annotations

import os
import subprocess
import sys
import argparse as ap
from dataclasses import dataclass, field

from mahkrab.tools.decorators.timers import compileruntime, compiletime
from mahkrab import constants as c
from mahkrab.tools.tooloverride import apply_tool_override

ASSEMBLY_LANGUAGE_KEY = 'assembly'
ASSEMBLY_DEFAULT_VARIANT = 'assembly_nasm'


@dataclass(frozen=True)
class AssemblyVariant:
    key: str
    label: str
    extensions: tuple[str, ...]
    aliases: tuple[str, ...]
    assembler_name: str
    supported_oses: tuple[str, ...]
    compile_mode: str
    link_mode_by_os: dict[str, str]
    object_format_by_os: dict[str, str] = field(default_factory=dict)
    preprocess_extensions: tuple[str, ...] = ()
    default_output_suffix_by_os: dict[str, str] = field(default_factory=dict)


ASSEMBLY_VARIANTS = {
    variant.key: variant
    for variant in (
        AssemblyVariant(
            key='assembly_nasm',
            label='Assembly (NASM)',
            extensions=('.asm', '.nasm'),
            aliases=('nasm',),
            assembler_name='Nasm',
            supported_oses=('unixlike',),
            compile_mode='nasm',
            link_mode_by_os={
                'unixlike': 'ld',
            },
            object_format_by_os={
                'unixlike': 'elf64',
            },
        ),
        AssemblyVariant(
            key='assembly_gas',
            label='Assembly (GNU assembler)',
            extensions=('.s', '.S'),
            aliases=('gas', 'gnu asm', 'gnu assembler'),
            assembler_name='GNU assembler',
            supported_oses=('unixlike',),
            compile_mode='gas',
            link_mode_by_os={
                'unixlike': 'ld',
            },
            object_format_by_os={
                'unixlike': '--64',
            },
            preprocess_extensions=('.S',),
        ),
    )
}
ASSEMBLY_LANGUAGE_KEYS = frozenset((ASSEMBLY_LANGUAGE_KEY, *ASSEMBLY_VARIANTS))
ASSEMBLY_LANGUAGE_ALIASES = {
    'assembly': ASSEMBLY_LANGUAGE_KEY,
    'asm': ASSEMBLY_LANGUAGE_KEY,
}
ASSEMBLY_EXTENSION_LANGUAGE_MAP: dict[str, str] = {}

for _variant in ASSEMBLY_VARIANTS.values():
    for _alias in _variant.aliases:
        ASSEMBLY_LANGUAGE_ALIASES[_alias] = _variant.key

    for _extension in _variant.extensions:
        ASSEMBLY_EXTENSION_LANGUAGE_MAP[_extension.lower()] = _variant.key


def get_language_aliases() -> dict[str, str]:
    return dict(ASSEMBLY_LANGUAGE_ALIASES)


def get_extension_language_map() -> dict[str, str]:
    return dict(ASSEMBLY_EXTENSION_LANGUAGE_MAP)


def is_assembly_language(language_key: str | None) -> bool:
    return bool(language_key in ASSEMBLY_LANGUAGE_KEYS)


def normalize_extension(full_path: str) -> str:
    return os.path.splitext(full_path)[1].lower()


def default_variant_key(full_path: str) -> str:
    return ASSEMBLY_EXTENSION_LANGUAGE_MAP.get(normalize_extension(full_path), ASSEMBLY_DEFAULT_VARIANT)


def resolve_variant(full_path: str, language_key: str | None) -> AssemblyVariant | None:
    variant_key = language_key
    if variant_key not in ASSEMBLY_VARIANTS:
        variant_key = default_variant_key(full_path)

    variant = ASSEMBLY_VARIANTS[variant_key]
    if c.osName not in variant.supported_oses:
        print(
            f"{c.Colours.MAGENTA}[MAHKRAB-CLI] -{c.Colours.ENDC} "
            f"{c.Colours.RED}Error:{c.Colours.ENDC} {variant.label} is not supported on {c.osName}."
        )
        return None

    return variant


def resolve_outputfile(outputfile: str, variant: AssemblyVariant) -> str:
    suffix = variant.default_output_suffix_by_os.get(c.osName, '')
    if suffix and not outputfile.endswith(suffix):
        return f'{outputfile}{suffix}'

    return outputfile


def native_run_cmd(outputfile: str, program_args: list[str]) -> list[str]:
    if c.osName == 'windows' or os.path.isabs(outputfile):
        run_cmd = [outputfile]
    else:
        run_cmd = [f'./{outputfile}']

    if program_args:
        run_cmd.extend(program_args)

    return run_cmd


def build_compile_command(
        variant: AssemblyVariant,
        full_path: str,
        objfile: str,
        compile_args: list[str],
        args: ap.Namespace,
    ) -> list[str]:
    if variant.compile_mode == 'nasm':
        object_format = variant.object_format_by_os[c.osName]
        cmd = [c.NASM_PATH, *compile_args, '-f', object_format, full_path, '-o', objfile]
        return apply_tool_override(cmd, args)

    if variant.compile_mode == 'gas':
        ext = os.path.splitext(full_path)[1]
        if ext in variant.preprocess_extensions:
            cmd = [c.GCC_PATH, *compile_args, '-c', full_path, '-o', objfile]
        else:
            object_format = variant.object_format_by_os.get(c.osName)
            cmd = [c.AS_PATH]
            if object_format:
                cmd.append(object_format)
            cmd.extend([*compile_args, full_path, '-o', objfile])

        return apply_tool_override(cmd, args)

    raise ValueError(f'Unsupported assembly compile mode: {variant.compile_mode}')


def build_link_command(variant: AssemblyVariant, objfile: str, outputfile: str) -> list[str]:
    link_mode = variant.link_mode_by_os[c.osName]

    if link_mode == 'ld':
        return [c.LD_PATH, '-o', outputfile, objfile]

    raise ValueError(f'Unsupported assembly link mode: {link_mode}')


def build_plan(
        full_path: str,
        outputfile: str,
        args: ap.Namespace,
        runOnCompile: bool,
        language_key: str | None,
    ) -> dict[str, object] | None:
    variant = resolve_variant(full_path, language_key)
    if variant is None:
        return None

    resolved_output = resolve_outputfile(outputfile, variant)
    objfile = f'{resolved_output}.o'
    compile_args = list(getattr(args, 'compileArgs', []))
    program_args = list(getattr(args, 'programArgs', []))

    compile_cmd = build_compile_command(variant, full_path, objfile, compile_args, args)
    link_cmd = build_link_command(variant, objfile, resolved_output)

    return {
        'language_key': variant.key,
        'language': variant.label,
        'outputfile': resolved_output,
        'objfile': objfile,
        'compile_cmd': compile_cmd,
        'link_cmd': link_cmd,
        'run_cmd': native_run_cmd(resolved_output, program_args) if runOnCompile else None,
    }


class Executor:
    @staticmethod
    def exec(full_path: str, outputfile: str, args: ap.Namespace, runOnCompile: bool) -> None:
        language_key = getattr(args, 'resolvedLanguage', None) or getattr(args, 'lang', None)
        plan = build_plan(full_path, outputfile, args, runOnCompile, language_key)
        if plan is None:
            return

        compile_cmd = list(plan['compile_cmd'])
        link_cmd = list(plan['link_cmd'])
        run_cmd = list(plan['run_cmd'] or [])
        toolchain_name = str(plan['language'])

        try:
            if runOnCompile:
                Executor.runOnCompile(compile_cmd, link_cmd, run_cmd)
            else:
                Executor.compile(compile_cmd, link_cmd)

        except subprocess.CalledProcessError as e:
            print(
                f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI] -{c.Colours.ENDC} {c.Colours.RED}"
                f"Error:{c.Colours.ENDC} Command failed with return code {c.Colours.RED}{e.returncode}{c.Colours.ENDC}.\n"
            )
        except FileNotFoundError:
            print(
                f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI] -{c.Colours.ENDC} {c.Colours.RED}"
                f"Error:{c.Colours.ENDC} The {toolchain_name} toolchain was not found.\n"
            )
        except Exception as e:
            print(
                f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI] -{c.Colours.ENDC} {c.Colours.RED}"
                f"Error:{c.Colours.ENDC} An unexpected error occured {c.Colours.RED}{e}{c.Colours.RED}.\n"
            )

    @staticmethod
    @compiletime
    def compile(compile_cmd: list[str], link_cmd: list[str]) -> None:
        subprocess.run(
            compile_cmd,
            check=True,
            stdout=sys.stdout,
            stderr=sys.stderr,
            text=True,
        )
        subprocess.run(
            link_cmd,
            check=True,
            stdout=sys.stdout,
            stderr=sys.stderr,
            text=True,
        )

    @staticmethod
    @compileruntime
    def runOnCompile(compile_cmd: list[str], link_cmd: list[str], run_cmd: list[str]) -> None:
        subprocess.run(
            compile_cmd,
            check=True,
            stdout=sys.stdout,
            stderr=sys.stderr,
            text=True,
        )
        subprocess.run(
            link_cmd,
            check=True,
            stdout=sys.stdout,
            stderr=sys.stderr,
            text=True,
        )
        subprocess.run(
            run_cmd,
            check=True,
            stdout=sys.stdout,
            stderr=sys.stderr,
            text=True,
        )
