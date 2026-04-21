from __future__ import annotations

import argparse as ap
import contextlib
import io
import os
import shlex
import shutil
from dataclasses import dataclass

from mahkrab import constants as c
from mahkrab.func import languages, plans
from mahkrab.tools.tooloverride import get_tool_override


@dataclass(frozen=True)
class ToolSpec:
    name: str
    attr: str
    env_var: str
    default: str


@dataclass(frozen=True)
class DiagnosticTarget:
    language_key: str
    filename: str
    label: str | None = None


@dataclass(frozen=True)
class CommandStatus:
    name: str
    value: str
    source: str
    available: bool
    resolved_path: str | None


@dataclass(frozen=True)
class LanguageStatus:
    language_key: str
    label: str
    commands: tuple[CommandStatus, ...]
    runnable: bool
    mode: str | None = None
    compile_command: str | None = None
    link_command: str | None = None
    run_command: str | None = None
 

TOOL_SPECS = {
    spec.attr: spec
    for spec in (
        ToolSpec('gcc', 'GCC_PATH', 'MAHKRAB_GCC', 'gcc'),
        ToolSpec('nasm', 'NASM_PATH', 'MAHKRAB_NASM', 'nasm'),
        ToolSpec('as', 'AS_PATH', 'MAHKRAB_AS', 'as'),
        ToolSpec('ld', 'LD_PATH', 'MAHKRAB_LD', 'ld'),
        ToolSpec('python', 'PYTHON_PATH', 'MAHKRAB_PYTHON', c.PYTHON_PATH),
        ToolSpec('g++', 'GPP_PATH', 'MAHKRAB_GPP', 'g++'),
        ToolSpec('rustc', 'RUSTC_PATH', 'MAHKRAB_RUSTC', 'rustc'),
        ToolSpec('go', 'GO_PATH', 'MAHKRAB_GO', 'go'),
        ToolSpec('javac', 'JAVAC_PATH', 'MAHKRAB_JAVAC', 'javac'),
        ToolSpec('java', 'JAVA_PATH', 'MAHKRAB_JAVA', 'java'),
        ToolSpec('node', 'NODE_PATH', 'MAHKRAB_NODE', 'node'),
        ToolSpec('ts-node', 'TS_NODE_PATH', 'MAHKRAB_TS', 'ts-node'),
        ToolSpec('ruby', 'RUBY_PATH', 'MAHKRAB_RUBY', 'ruby'),
        ToolSpec('php', 'PHP_PATH', 'MAHKRAB_PHP', 'php'),
        ToolSpec('lua', 'LUA_PATH', 'MAHKRAB_LUA', 'lua'),
        ToolSpec('bash', 'BASH_PATH', 'MAHKRAB_BASH', 'bash'),
        ToolSpec('pwsh', 'PWSH_PATH', 'MAHKRAB_PWSH', 'pwsh'),
        ToolSpec('perl', 'PERL_PATH', 'MAHKRAB_PERL', 'perl'),
        ToolSpec('csc', 'CSC_PATH', 'MAHKRAB_CSC', 'csc'),
        ToolSpec('vbc', 'VBC_PATH', 'MAHKRAB_VBC', 'vbc'),
        ToolSpec('mono', 'MONO_PATH', 'MAHKRAB_MONO', 'mono'),
        ToolSpec('sqlite3', 'SQLITE3_PATH', 'MAHKRAB_SQLITE3', 'sqlite3'),
        ToolSpec('Rscript', 'RSCRIPT_PATH', 'MAHKRAB_RSCRIPT', 'Rscript'),
        ToolSpec('fpc', 'FPC_PATH', 'MAHKRAB_FPC', 'fpc'),
        ToolSpec('twcli', 'TURBOWARP_PATH', 'MAHKRAB_TURBOWARP', 'twcli'),
        ToolSpec('gfortran', 'GFORTRAN_PATH', 'MAHKRAB_GFORTRAN', 'gfortran'),
        ToolSpec('matlab', 'MATLAB_PATH', 'MAHKRAB_MATLAB', 'matlab'),
        ToolSpec('gnatmake', 'GNATMAKE_PATH', 'MAHKRAB_GNATMAKE', 'gnatmake'),
        ToolSpec('swiftc', 'SWIFTC_PATH', 'MAHKRAB_SWIFTC', 'swiftc'),
        ToolSpec('swipl', 'SWIPL_PATH', 'MAHKRAB_SWIPL', 'swipl'),
        ToolSpec('kotlinc', 'KOTLINC_PATH', 'MAHKRAB_KOTLINC', 'kotlinc'),
        ToolSpec('fbc', 'FBC_PATH', 'MAHKRAB_FBC', 'fbc'),
        ToolSpec('cobc', 'COBC_PATH', 'MAHKRAB_COBC', 'cobc'),
        ToolSpec('dart', 'DART_PATH', 'MAHKRAB_DART', 'dart'),
    )
}


LANGUAGE_TARGETS = (
    DiagnosticTarget('python', 'doctor.py'),
    DiagnosticTarget('c', 'doctor.c'),
    DiagnosticTarget('cpp', 'doctor.cpp'),
    DiagnosticTarget('java', 'Doctor.java'),
    DiagnosticTarget('csharp', 'doctor.cs'),
    DiagnosticTarget('javascript', 'doctor.js'),
    DiagnosticTarget('typescript', 'doctor.ts'),
    DiagnosticTarget('visual_basic', 'doctor.vb'),
    DiagnosticTarget('sql', 'doctor.sql'),
    DiagnosticTarget('r', 'doctor.r'),
    DiagnosticTarget('pascal', 'doctor.pas'),
    DiagnosticTarget('perl', 'doctor.pl'),
    DiagnosticTarget('scratch', 'doctor.sb3'),
    DiagnosticTarget('fortran', 'doctor.f90'),
    DiagnosticTarget('rust', 'doctor.rs'),
    DiagnosticTarget('matlab', 'doctor.m'),
    DiagnosticTarget('go', 'doctor.go'),
    DiagnosticTarget('assembly_nasm', 'doctor.asm'),
    DiagnosticTarget('assembly_gas', 'doctor.s'),
    DiagnosticTarget('php', 'doctor.php'),
    DiagnosticTarget('ada', 'doctor.adb'),
    DiagnosticTarget('swift', 'doctor.swift'),
    DiagnosticTarget('prolog', 'doctor.pro'),
    DiagnosticTarget('kotlin', 'doctor.kt'),
    DiagnosticTarget('classic_visual_basic', 'doctor.bas'),
    DiagnosticTarget('cobol', 'doctor.cob'),
    DiagnosticTarget('dart', 'doctor.dart'),
    DiagnosticTarget('ruby', 'doctor.rb'),
    DiagnosticTarget('lua', 'doctor.lua'),
    DiagnosticTarget('bash', 'doctor.sh'),
    DiagnosticTarget('powershell', 'doctor.ps1'),
)


COMPILE_TOOL_ATTRS = {
    'c': ('GCC_PATH',),
    'cpp': ('GPP_PATH',),
    'rust': ('RUSTC_PATH',),
    'go': ('GO_PATH',),
    'java': ('JAVAC_PATH',),
    'assembly_nasm': ('NASM_PATH',),
    'assembly_gas': ('AS_PATH',),
    'csharp': ('CSC_PATH',),
    'visual_basic': ('VBC_PATH',),
    'pascal': ('FPC_PATH',),
    'fortran': ('GFORTRAN_PATH',),
    'ada': ('GNATMAKE_PATH',),
    'swift': ('SWIFTC_PATH',),
    'kotlin': ('KOTLINC_PATH',),
    'classic_visual_basic': ('FBC_PATH',),
    'cobol': ('COBC_PATH',),
}
LINK_TOOL_ATTRS = {
    'assembly_nasm': ('LD_PATH',),
    'assembly_gas': ('LD_PATH',),
}
RUN_TOOL_ATTRS = {
    'python': 'PYTHON_PATH',
    'java': 'JAVA_PATH',
    'csharp': 'MONO_PATH',
    'visual_basic': 'MONO_PATH',
    'javascript': 'NODE_PATH',
    'typescript': 'TS_NODE_PATH',
    'ruby': 'RUBY_PATH',
    'php': 'PHP_PATH',
    'lua': 'LUA_PATH',
    'bash': 'BASH_PATH',
    'powershell': 'PWSH_PATH',
    'perl': 'PERL_PATH',
    'sql': 'SQLITE3_PATH',
    'r': 'RSCRIPT_PATH',
    'scratch': 'TURBOWARP_PATH',
    'matlab': 'MATLAB_PATH',
    'prolog': 'SWIPL_PATH',
    'kotlin': 'JAVA_PATH',
    'dart': 'DART_PATH',
}
EXTRA_TOOL_ATTRS = {
    # .S sources use gcc as a preprocessor driver before the GAS path links with ld.
    'assembly_gas': ('GCC_PATH',),
}
LANGUAGE_OVERRIDE_VALUES = {
    'assembly_nasm': 'nasm',
    'assembly_gas': 'gas',
}
TOOL_OVERRIDE_LANGUAGES = {
    'python',
    'c',
    'cpp',
    'rust',
    'go',
    'java',
    'assembly_nasm',
    'assembly_gas',
    'csharp',
    'visual_basic',
    'pascal',
    'fortran',
    'ada',
    'swift',
    'kotlin',
    'classic_visual_basic',
    'cobol',
    'javascript',
    'typescript',
    'ruby',
    'php',
    'lua',
    'bash',
    'powershell',
    'perl',
    'sql',
    'r',
    'scratch',
    'matlab',
    'prolog',
    'dart',
}


def source_for_attr(attr: str, command_value: str, args: ap.Namespace) -> tuple[str, str]:
    if attr == 'PYTHON_PATH':
        return str(getattr(args, 'pythonCmd', command_value)), setting_source(args, 'pythonCmd', 'default')

    spec = TOOL_SPECS[attr]
    env_value = os.environ.get(spec.env_var)
    if env_value == command_value:
        return command_value, f'environment variable {spec.env_var}'

    return command_value, 'default'


def setting_source(args: ap.Namespace, key: str, default: str) -> str:
    sources = getattr(args, 'sources', {})
    if isinstance(sources, dict):
        return str(sources.get(key, default))

    return default


def status_for_command(
        attr: str,
        command_value: str,
        args: ap.Namespace,
        supports_tool_override: bool,
    ) -> CommandStatus:

    tool_override = get_tool_override(args)
    if supports_tool_override and tool_override and command_value == tool_override[0]:
        value = shlex.join(tool_override)
        source = setting_source(args, 'tool', 'configured tool override')
    else:
        value, source = source_for_attr(attr, command_value, args)

    resolved_path = shutil.which(command_value)
    spec = TOOL_SPECS[attr]
    return CommandStatus(
        name=spec.name,
        value=value,
        source=source,
        available=resolved_path is not None,
        resolved_path=resolved_path,
    )


def first_command_token(cmd: object) -> str | None:
    if not isinstance(cmd, list) or not cmd:
        return None

    return str(cmd[0])


def is_generated_run_target(command: str, plan: dict[str, object]) -> bool:
    outputfile = plan.get('outputfile')
    if not outputfile:
        return False

    output = str(outputfile)
    generated_paths = {output, f'./{output}'}
    if output.endswith('.jar'):
        generated_paths.add(output)
    elif not output.endswith('.jar'):
        generated_paths.add(f'{output}.jar')

    return command in generated_paths


def plan_for_target(target: DiagnosticTarget, args: ap.Namespace) -> dict[str, object] | None:
    diagnostic_args = ap.Namespace(**vars(args))
    diagnostic_args.lang = LANGUAGE_OVERRIDE_VALUES.get(target.language_key, target.language_key)
    diagnostic_args.targetfile = target.filename
    diagnostic_args.outputfile = os.path.join('build', os.path.splitext(target.filename)[0])

    with contextlib.redirect_stdout(io.StringIO()):
        return plans.build_execution_plan(
            target.filename,
            diagnostic_args.outputfile,
            diagnostic_args,
            True,
        )


def diagnose_language(target: DiagnosticTarget, args: ap.Namespace) -> LanguageStatus:
    plan = plan_for_target(target, args)
    label = target.label or languages.LANGUAGE_LABELS.get(target.language_key, target.language_key)
    if plan is None:
        return LanguageStatus(target.language_key, label, (), False)

    language_key = str(plan.get('language_key', target.language_key))
    label = target.label or str(plan.get('language', label))
    commands: list[CommandStatus] = []

    compile_cmd = first_command_token(plan.get('compile_cmd'))
    for attr in COMPILE_TOOL_ATTRS.get(language_key, ()):
        if compile_cmd:
            commands.append(
                status_for_command(
                    attr,
                    compile_cmd,
                    args,
                    language_key in TOOL_OVERRIDE_LANGUAGES,
                )
            )

    link_cmd = first_command_token(plan.get('link_cmd'))
    for attr in LINK_TOOL_ATTRS.get(language_key, ()):
        if link_cmd:
            commands.append(status_for_command(attr, link_cmd, args, False))

    run_cmd = first_command_token(plan.get('run_cmd'))
    run_attr = RUN_TOOL_ATTRS.get(language_key)
    if run_cmd and run_attr and not is_generated_run_target(run_cmd, plan):
        commands.append(
            status_for_command(
                run_attr,
                run_cmd,
                args,
                language_key in TOOL_OVERRIDE_LANGUAGES,
            )
        )

    for attr in EXTRA_TOOL_ATTRS.get(language_key, ()):
        command_value = str(getattr(c, attr))
        commands.append(status_for_command(attr, command_value, args, False))

    commands = list(dict.fromkeys(commands))
    return LanguageStatus(
        language_key,
        label,
        tuple(commands),
        bool(commands and all(command.available for command in commands)),
        str(plan.get('mode') or ''),
        plans.format_command(plan.get('compile_cmd')),
        plans.format_command(plan.get('link_cmd')),
        plans.format_command(plan.get('run_cmd')),
    )


def diagnose(args: ap.Namespace) -> tuple[LanguageStatus, ...]:
    return tuple(diagnose_language(target, args) for target in LANGUAGE_TARGETS)


def status_text(ok: bool) -> str:
    colour = c.Colours.GREEN if ok else c.Colours.RED
    label = 'ok' if ok else 'missing'
    return f'{colour}{label}{c.Colours.ENDC}'


def available_text(available: bool) -> str:
    colour = c.Colours.GREEN if available else c.Colours.RED
    label = 'yes' if available else 'no'
    return f'{colour}{label}{c.Colours.ENDC}'


def doctor_mode(args: ap.Namespace) -> str:
    if getattr(args, 'doctorQuiet', False):
        return 'quiet'
    if getattr(args, 'doctorVerbose', False):
        return 'verbose'

    return 'default'


def print_summary(unavailable: list[str]) -> None:
    if unavailable:
        print(
            f'{c.Colours.MAGENTA}[MAHKRAB-CLI] -{c.Colours.ENDC} '
            f'{c.Colours.RED}Unavailable languages:{c.Colours.ENDC} {", ".join(unavailable)}'
        )
    else:
        print(
            f'{c.Colours.MAGENTA}[MAHKRAB-CLI] -{c.Colours.ENDC} '
            f'{c.Colours.GREEN}All supported languages are runnable.{c.Colours.ENDC}'
        )


def print_report(statuses: tuple[LanguageStatus, ...], args: ap.Namespace) -> None:
    unavailable = [status.label for status in statuses if not status.runnable]
    if getattr(args, 'doctorQuiet', False):
        print_summary(unavailable)
        return

    config_path = getattr(args, 'configPath', None) or 'none'
    verbose = bool(getattr(args, 'doctorVerbose', False))
    mode_source = setting_source(args, 'doctorMode', 'default')
    print(f'{c.Colours.MAGENTA}[MAHKRAB-CLI]{c.Colours.ENDC} Doctor')
    print(f'  config: {config_path}')
    print(f'  cwd: {os.getcwd()}')
    print(f'  doctor mode: {doctor_mode(args)} ({mode_source})')

    for status in statuses:
        print(f'  {c.Colours.CYAN}{status.label}{c.Colours.ENDC}: {status_text(status.runnable)}')
        if not status.commands:
            print(f'    - {c.Colours.RED}no supported toolchain commands found{c.Colours.ENDC}')
        else:
            for command in status.commands:
                available = available_text(command.available)
                resolved_path = command.resolved_path or '-'
                print(
                    f'    - {c.Colours.BLUE}{command.name}{c.Colours.ENDC}: value={command.value} '
                    f'source={command.source} available={available} path={resolved_path}'
                )

        if verbose:
            print(f'    mode: {status.mode or "-"}')
            print(f'    compile command: {status.compile_command or "-"}')
            print(f'    link command: {status.link_command or "-"}')
            print(f'    run command: {status.run_command or "-"}')

    print_summary(unavailable)


def run(args: ap.Namespace) -> int:
    statuses = diagnose(args)
    print_report(statuses, args)
    return 0 if all(status.runnable for status in statuses) else 1
