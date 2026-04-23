from __future__ import annotations

import argparse as ap
import contextlib
import io
import json
import os
import shlex
import shutil
from dataclasses import dataclass

from mahkrab import constants as c
from mahkrab.func import languages, plans
from mahkrab.tools.targetos import detectHostOs
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
    command: str
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


@dataclass(frozen=True)
class DiagnosticSelection:
    targets: tuple[DiagnosticTarget, ...]
    all_languages: bool = False


@dataclass(frozen=True)
class InstallHints:
    linux: tuple[str, ...]
    macos: tuple[str, ...]
    windows: tuple[str, ...]

    def as_dict(self, target_os: str | None = None) -> dict[str, list[str]]:
        if target_os is not None:
            values = {
                'linux': self.linux,
                'macos': self.macos,
                'windows': self.windows,
            }.get(target_os, ())
            return {target_os: list(values)}

        return {
            'linux': list(self.linux),
            'macos': list(self.macos),
            'windows': list(self.windows),
        }

    def recommended(self, detected_os: str) -> str | None:
        options = {
            'linux': self.linux,
            'macos': self.macos,
            'windows': self.windows,
        }.get(detected_os, ())
        if options:
            return options[0]

        return None


@dataclass(frozen=True)
class ToolReport:
    tool: str
    command: str
    value: str
    source: str
    status: str
    languages: tuple[str, ...]
    language_labels: tuple[str, ...]
    resolved_path: str | None
    install_hints: InstallHints
    recommended_hint: str | None


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


GNU_BUILD_HINTS = InstallHints(
    linux=('sudo apt install build-essential',),
    macos=('xcode-select --install',),
    windows=('Install MSYS2 or Visual Studio Build Tools and add the compiler bin directory to PATH',),
)
BINUTILS_HINTS = InstallHints(
    linux=('sudo apt install binutils',),
    macos=('xcode-select --install',),
    windows=('Install MSYS2 binutils or Visual Studio Build Tools and add them to PATH',),
)
PYTHON_HINTS = InstallHints(
    linux=('sudo apt install python3',),
    macos=('brew install python',),
    windows=('Install Python from python.org and enable Add python.exe to PATH',),
)
RUST_HINTS = InstallHints(
    linux=('curl https://sh.rustup.rs -sSf | sh',),
    macos=('brew install rustup-init && rustup-init',),
    windows=('Install Rust with rustup-init.exe and let it update PATH',),
)
GO_HINTS = InstallHints(
    linux=('sudo apt install golang',),
    macos=('brew install go',),
    windows=('winget install GoLang.Go',),
)
JAVA_HINTS = InstallHints(
    linux=('sudo apt install default-jdk',),
    macos=('brew install openjdk',),
    windows=('Install a JDK such as Eclipse Temurin and add it to PATH',),
)
NODE_HINTS = InstallHints(
    linux=('sudo apt install nodejs npm',),
    macos=('brew install node',),
    windows=('winget install OpenJS.NodeJS.LTS',),
)
TS_NODE_HINTS = InstallHints(
    linux=('sudo npm install -g ts-node typescript',),
    macos=('npm install -g ts-node typescript',),
    windows=('Install Node.js, then run npm install -g ts-node typescript',),
)
RUBY_HINTS = InstallHints(
    linux=('sudo apt install ruby-full',),
    macos=('brew install ruby',),
    windows=('Install RubyInstaller for Windows and add Ruby to PATH',),
)
PHP_HINTS = InstallHints(
    linux=('sudo apt install php',),
    macos=('brew install php',),
    windows=('winget install PHP.PHP',),
)
LUA_HINTS = InstallHints(
    linux=('sudo apt install lua5.4',),
    macos=('brew install lua',),
    windows=('Install Lua for Windows and add it to PATH',),
)
BASH_HINTS = InstallHints(
    linux=('sudo apt install bash',),
    macos=('brew install bash',),
    windows=('Use Git Bash, WSL, or MSYS2 and ensure bash.exe is on PATH',),
)
PWSH_HINTS = InstallHints(
    linux=('sudo apt install powershell',),
    macos=('brew install --cask powershell',),
    windows=('winget install Microsoft.PowerShell',),
)
PERL_HINTS = InstallHints(
    linux=('sudo apt install perl',),
    macos=('brew install perl',),
    windows=('Install Strawberry Perl and add perl to PATH',),
)
DOTNET_SDK_HINTS = InstallHints(
    linux=('sudo apt install dotnet-sdk-8.0',),
    macos=('brew install --cask dotnet-sdk',),
    windows=('winget install Microsoft.DotNet.SDK.8',),
)
MONO_HINTS = InstallHints(
    linux=('sudo apt install mono-complete',),
    macos=('brew install mono',),
    windows=('Install Mono and add mono to PATH',),
)
SQLITE_HINTS = InstallHints(
    linux=('sudo apt install sqlite3',),
    macos=('brew install sqlite',),
    windows=('winget install SQLite.SQLite',),
)
RSCRIPT_HINTS = InstallHints(
    linux=('sudo apt install r-base',),
    macos=('brew install --cask r',),
    windows=('Install R from CRAN and add Rscript to PATH',),
)
PASCAL_HINTS = InstallHints(
    linux=('sudo apt install fp-compiler',),
    macos=('brew install fpc',),
    windows=('Install Free Pascal and add fpc to PATH',),
)
TURBOWARP_HINTS = InstallHints(
    linux=('npm install -g twcli',),
    macos=('npm install -g twcli',),
    windows=('Install Node.js, then run npm install -g twcli',),
)
FORTRAN_HINTS = InstallHints(
    linux=('sudo apt install gfortran',),
    macos=('brew install gcc',),
    windows=('Install MSYS2 or MinGW-w64 with gfortran and add it to PATH',),
)
MATLAB_HINTS = InstallHints(
    linux=('Install MATLAB and add its bin directory to PATH',),
    macos=('Install MATLAB and add its bin directory to PATH',),
    windows=('Install MATLAB and add matlab.exe to PATH',),
)
ADA_HINTS = InstallHints(
    linux=('sudo apt install gnat',),
    macos=('brew install gcc',),
    windows=('Install GNAT or MSYS2 GCC Ada support and add gnatmake to PATH',),
)
SWIFT_HINTS = InstallHints(
    linux=('Install Swift from swift.org and add swiftc to PATH',),
    macos=('xcode-select --install',),
    windows=('Install Swift for Windows and add swiftc to PATH',),
)
PROLOG_HINTS = InstallHints(
    linux=('sudo apt install swi-prolog',),
    macos=('brew install swi-prolog',),
    windows=('Install SWI-Prolog and add swipl to PATH',),
)
KOTLIN_HINTS = InstallHints(
    linux=('sudo apt install kotlin default-jdk',),
    macos=('brew install kotlin openjdk',),
    windows=('Install Kotlin and a JDK, then add kotlinc and java to PATH',),
)
FREEBASIC_HINTS = InstallHints(
    linux=('Install FreeBASIC and add fbc to PATH',),
    macos=('Install FreeBASIC and add fbc to PATH',),
    windows=('Install FreeBASIC and add fbc.exe to PATH',),
)
COBOL_HINTS = InstallHints(
    linux=('sudo apt install gnucobol',),
    macos=('brew install gnu-cobol',),
    windows=('Install GnuCOBOL and add cobc to PATH',),
)
DART_HINTS = InstallHints(
    linux=('sudo apt install dart',),
    macos=('brew install dart',),
    windows=('winget install Dart.DartSDK',),
)
NASM_HINTS = InstallHints(
    linux=('sudo apt install nasm',),
    macos=('brew install nasm',),
    windows=('winget install NASM.NASM',),
)
CLANG_HINTS = InstallHints(
    linux=('sudo apt install clang',),
    macos=('xcode-select --install',),
    windows=('Install LLVM or Visual Studio Build Tools and add clang to PATH',),
)
GENERIC_INSTALL_HINTS = InstallHints(
    linux=('Install the tool with your package manager and add it to PATH',),
    macos=('Install the tool with Homebrew or the vendor package and add it to PATH',),
    windows=('Install the tool and ensure its executable directory is on PATH',),
)

INSTALL_HINTS = {
    'gcc': GNU_BUILD_HINTS,
    'g++': GNU_BUILD_HINTS,
    'clang': CLANG_HINTS,
    'clang++': CLANG_HINTS,
    'as': BINUTILS_HINTS,
    'ld': BINUTILS_HINTS,
    'python': PYTHON_HINTS,
    'rustc': RUST_HINTS,
    'go': GO_HINTS,
    'javac': JAVA_HINTS,
    'java': JAVA_HINTS,
    'node': NODE_HINTS,
    'ts-node': TS_NODE_HINTS,
    'ruby': RUBY_HINTS,
    'php': PHP_HINTS,
    'lua': LUA_HINTS,
    'bash': BASH_HINTS,
    'pwsh': PWSH_HINTS,
    'perl': PERL_HINTS,
    'csc': DOTNET_SDK_HINTS,
    'vbc': DOTNET_SDK_HINTS,
    'mono': MONO_HINTS,
    'sqlite3': SQLITE_HINTS,
    'rscript': RSCRIPT_HINTS,
    'fpc': PASCAL_HINTS,
    'twcli': TURBOWARP_HINTS,
    'gfortran': FORTRAN_HINTS,
    'matlab': MATLAB_HINTS,
    'gnatmake': ADA_HINTS,
    'swiftc': SWIFT_HINTS,
    'swipl': PROLOG_HINTS,
    'kotlinc': KOTLIN_HINTS,
    'fbc': FREEBASIC_HINTS,
    'cobc': COBOL_HINTS,
    'dart': DART_HINTS,
    'nasm': NASM_HINTS,
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


def print_error(message: str) -> None:
    print(
        f'{c.Colours.MAGENTA}[MAHKRAB-CLI] -{c.Colours.ENDC} '
        f'{c.Colours.RED}Error:{c.Colours.ENDC} {message}'
    )


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
        command=command_value,
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
    selection = getattr(args, 'doctorSelection', DiagnosticSelection(LANGUAGE_TARGETS, all_languages=True))
    return tuple(diagnose_language(target, args) for target in selection.targets)


def parse_language_names(value: str) -> tuple[str, ...]:
    return tuple(part.strip() for part in str(value).split(',') if part.strip())


def target_for_language(language_key: str, targetfile: str | None = None) -> DiagnosticTarget | None:
    target_map = {target.language_key: target for target in LANGUAGE_TARGETS}
    if language_key == 'assembly':
        if targetfile:
            ext = os.path.splitext(str(targetfile))[1].lower()
            target_language = languages.EXTENSION_LANGUAGE_MAP.get(ext)
            if target_language in target_map:
                return target_map[target_language]

        return target_map.get('assembly_nasm')

    return target_map.get(language_key)


def selection_from_language_names(
        value: str,
        targetfile: str | None = None,
    ) -> tuple[DiagnosticSelection | None, str | None]:
    targets: list[DiagnosticTarget] = []
    seen: set[str] = set()

    for name in parse_language_names(value):
        language_key = languages.normalize_language(name)
        if language_key is None:
            return None, f'Unsupported doctor language: {name}'

        target = target_for_language(language_key, targetfile)
        if target is None:
            label = languages.LANGUAGE_LABELS.get(language_key, language_key)
            return None, f'Doctor does not support language: {label}'

        if target.language_key not in seen:
            targets.append(target)
            seen.add(target.language_key)

    if not targets:
        return None, 'Doctor needs at least one language after --lang.'

    return DiagnosticSelection(tuple(targets)), None


def selection_from_target(args: ap.Namespace) -> tuple[DiagnosticSelection | None, str | None]:
    targetfile = getattr(args, 'targetfile', None)
    if not targetfile:
        return None, 'Doctor needs a target, --lang, or --all.'

    ext = os.path.splitext(str(targetfile))[1].lower()
    language_key = languages.EXTENSION_LANGUAGE_MAP.get(ext)
    if language_key is None:
        return None, f'Doctor could not resolve a language for target: {targetfile}'

    target = target_for_language(language_key)
    if target is None:
        label = languages.LANGUAGE_LABELS.get(language_key, language_key)
        return None, f'Doctor does not support language: {label}'

    return DiagnosticSelection((target,)), None


def select_targets(args: ap.Namespace) -> tuple[DiagnosticSelection | None, str | None]:
    if getattr(args, 'doctorAll', False):
        return DiagnosticSelection(LANGUAGE_TARGETS, all_languages=True), None

    if getattr(args, 'lang', None):
        return selection_from_language_names(str(getattr(args, 'lang')), getattr(args, 'targetfile', None))

    return selection_from_target(args)


def target_os(args: ap.Namespace) -> str:
    return str(getattr(args, 'targetOs', None) or detectHostOs())


def normalized_tool_key(command: str) -> str:
    tool_name = os.path.basename(str(command)).lower()
    if tool_name.endswith('.exe'):
        tool_name = tool_name[:-4]

    if tool_name.startswith('python'):
        return 'python'
    if tool_name.startswith('rscript'):
        return 'rscript'
    if tool_name.startswith('clang++'):
        return 'clang++'
    if tool_name.startswith('clang'):
        return 'clang'
    if tool_name.startswith('javac'):
        return 'javac'
    if tool_name.startswith('java'):
        return 'java'

    return tool_name


def install_hints_for_command(command: CommandStatus) -> InstallHints:
    for key in (normalized_tool_key(command.command), normalized_tool_key(command.name)):
        hints = INSTALL_HINTS.get(key)
        if hints is not None:
            return hints

    return GENERIC_INSTALL_HINTS


def build_tool_reports(statuses: tuple[LanguageStatus, ...], detected_os: str) -> tuple[ToolReport, ...]:
    grouped: dict[
        tuple[str, str, str, str, bool, str | None],
        dict[str, set[str] | CommandStatus],
    ] = {}

    for status in statuses:
        for command in status.commands:
            key = (
                command.name,
                command.command,
                command.value,
                command.source,
                command.available,
                command.resolved_path,
            )
            entry = grouped.setdefault(
                key,
                {
                    'command_status': command,
                    'languages': set(),
                    'language_labels': set(),
                },
            )
            languages_seen = entry['languages']
            labels_seen = entry['language_labels']
            assert isinstance(languages_seen, set)
            assert isinstance(labels_seen, set)
            languages_seen.add(status.language_key)
            labels_seen.add(status.label)

    reports: list[ToolReport] = []
    for _, entry in grouped.items():
        command = entry['command_status']
        assert isinstance(command, CommandStatus)
        languages_seen = entry['languages']
        labels_seen = entry['language_labels']
        assert isinstance(languages_seen, set)
        assert isinstance(labels_seen, set)
        hints = install_hints_for_command(command)
        status = 'installed' if command.available else 'missing'
        reports.append(
            ToolReport(
                tool=command.name,
                command=command.command,
                value=command.value,
                source=command.source,
                status=status,
                languages=tuple(sorted(languages_seen)),
                language_labels=tuple(sorted(labels_seen)),
                resolved_path=command.resolved_path,
                install_hints=hints,
                recommended_hint=hints.recommended(detected_os) if not command.available else None,
            )
        )

    return tuple(sorted(reports, key=lambda report: (report.status, report.tool, report.command)))


def json_language_list() -> list[dict[str, object]]:
    language_entries: list[dict[str, object]] = []
    for target in LANGUAGE_TARGETS:
        aliases = list(languages.aliases_for_language(target.language_key))
        if target.language_key == 'assembly_nasm':
            aliases.extend(languages.aliases_for_language('assembly'))

        label = target.label or languages.LANGUAGE_LABELS.get(target.language_key, target.language_key)
        language_entries.append(
            {
                'language': target.language_key,
                'label': label,
                'aliases': list(dict.fromkeys(aliases)),
            }
        )

    return language_entries


def print_languages() -> None:
    print(f'{c.Colours.MAGENTA}[MAHKRAB-CLI]{c.Colours.ENDC} Doctor languages')
    for entry in json_language_list():
        alias_text = ', '.join(entry['aliases']) or str(entry['language'])
        print(
            f'  {c.Colours.CYAN}{entry["label"]}{c.Colours.ENDC}: '
            f'{c.Colours.BLUE}{alias_text}{c.Colours.ENDC}'
        )


def summary_success_message(all_languages: bool) -> str:
    if all_languages:
        return 'All supported languages are runnable.'

    return 'All checked languages are runnable.'


def unavailable_label(all_languages: bool) -> str:
    if all_languages:
        return 'Unavailable languages'

    return 'Unavailable checked languages'


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


def print_summary(unavailable: list[str], all_languages: bool) -> None:
    if unavailable:
        print(
            f'{c.Colours.MAGENTA}[MAHKRAB-CLI] -{c.Colours.ENDC} '
            f'{c.Colours.RED}{unavailable_label(all_languages)}:{c.Colours.ENDC} {", ".join(unavailable)}'
        )
    else:
        print(
            f'{c.Colours.MAGENTA}[MAHKRAB-CLI] -{c.Colours.ENDC} '
            f'{c.Colours.GREEN}{summary_success_message(all_languages)}{c.Colours.ENDC}'
        )


def display_tool_name(report: ToolReport) -> str:
    if report.command != report.tool:
        return f'{report.command} ({report.tool})'

    return report.tool


def print_missing_tools(tool_reports: tuple[ToolReport, ...], detected_os: str) -> None:
    missing_reports = [report for report in tool_reports if report.status == 'missing']
    if not missing_reports:
        return

    print(f'  {c.Colours.YELLOW}Missing tools:{c.Colours.ENDC}')
    for report in missing_reports:
        language_text = ', '.join(report.language_labels)
        install_hint = report.recommended_hint or 'Install the tool and add it to PATH'
        print(
            f'    - {c.Colours.BLUE}{display_tool_name(report)}{c.Colours.ENDC}: '
            f'languages={language_text} '
            f'install ({detected_os})={c.Colours.YELLOW}{install_hint}{c.Colours.ENDC}'
        )


def render_json_report(
        statuses: tuple[LanguageStatus, ...],
        args: ap.Namespace,
        error: str | None = None,
    ) -> dict[str, object]:
    effective_os = target_os(args)
    if error is not None:
        return {
            'ok': False,
            'os': effective_os,
            'detected_os': detectHostOs(),
            'os_source': setting_source(args, 'targetOs', 'detected host OS'),
            'checked_languages': [],
            'checked_tools': [],
            'error': error,
        }

    selection = getattr(args, 'doctorSelection', DiagnosticSelection((), all_languages=False))
    tool_reports = build_tool_reports(statuses, effective_os)
    return {
        'ok': all(status.runnable for status in statuses),
        'os': effective_os,
        'detected_os': detectHostOs(),
        'os_source': setting_source(args, 'targetOs', 'detected host OS'),
        'checked_languages': [target.language_key for target in selection.targets],
        'checked_tools': [
            {
                'tool': report.tool,
                'command': report.command,
                'status': report.status,
                'languages': list(report.languages),
                'resolved_path': report.resolved_path,
                'value': report.value,
                'source': report.source,
                'install_hints': report.install_hints.as_dict(effective_os),
                'recommended_hint': report.recommended_hint,
            }
            for report in tool_reports
        ],
    }


def print_json_report(report: dict[str, object]) -> None:
    print(json.dumps(report, indent=2, sort_keys=True))


def print_report(statuses: tuple[LanguageStatus, ...], args: ap.Namespace) -> None:
    unavailable = [status.label for status in statuses if not status.runnable]
    selection = getattr(args, 'doctorSelection', DiagnosticSelection(LANGUAGE_TARGETS, all_languages=True))
    effective_os = target_os(args)
    tool_reports = build_tool_reports(statuses, effective_os)
    if getattr(args, 'doctorQuiet', False):
        print_summary(unavailable, selection.all_languages)
        print_missing_tools(tool_reports, effective_os)
        return

    config_path = getattr(args, 'configPath', None) or 'none'
    verbose = bool(getattr(args, 'doctorVerbose', False))
    mode_source = setting_source(args, 'doctorMode', 'default')
    print(f'{c.Colours.MAGENTA}[MAHKRAB-CLI]{c.Colours.ENDC} Doctor')
    print(f'  config: {config_path}')
    print(f'  cwd: {os.getcwd()}')
    print(f'  doctor mode: {doctor_mode(args)} ({mode_source})')
    print(f'  hint os: {effective_os} ({setting_source(args, "targetOs", "detected host OS")})')

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

    print_missing_tools(tool_reports, effective_os)
    print_summary(unavailable, selection.all_languages)


def run(args: ap.Namespace) -> int:
    if getattr(args, 'doctorLanguages', False):
        if getattr(args, 'doctorJson', False):
            print_json_report(
                {
                    'ok': True,
                    'os': target_os(args),
                    'detected_os': detectHostOs(),
                    'os_source': setting_source(args, 'targetOs', 'detected host OS'),
                    'languages': json_language_list(),
                }
            )
        else:
            print_languages()
        return 0

    selection, error = select_targets(args)
    if error:
        if getattr(args, 'doctorJson', False):
            print_json_report(render_json_report((), args, error))
        else:
            print_error(error)
        return 2

    setattr(args, 'doctorSelection', selection)
    statuses = diagnose(args)
    if getattr(args, 'doctorJson', False):
        print_json_report(render_json_report(statuses, args))
    else:
        print_report(statuses, args)

    return 0 if all(status.runnable for status in statuses) else 1
