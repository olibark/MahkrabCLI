import os
import shlex
import argparse as ap

from mahkrab import constants as c
from mahkrab.func.executors.compiled import (
    cexec, binexec, asmexec, cppexec,
    rustexec, goexec, javaexec, cmdexec
)
from mahkrab.func.executors.interpreted import (
    pyexec, interpexec, sqlexec
)
from mahkrab.tools.tooloverride import apply_tool_override, get_tool_override

SUPPORTED_LANGUAGES = (
    'Python',
    'C',
    'C++',
    'Java',
    'C#',
    'JavaScript',
    'Visual Basic',
    'SQL',
    'R',
    'Delphi/Object Pascal',
    'Perl',
    'Scratch',
    'Fortran',
    'Rust',
    'MATLAB',
    'Go',
    'Assembly',
    'PHP',
    'Ada',
    'Swift',
    'Prolog',
    'Kotlin',
    'Classic Visual Basic',
    'COBOL',
    'Dart',
)

LANGUAGE_ALIASES = {
    'python': 'python',
    'py': 'python',
    'c': 'c',
    'cpp': 'cpp',
    'c++': 'cpp',
    'cxx': 'cpp',
    'cc': 'cpp',
    'java': 'java',
    'c#': 'csharp',
    'csharp': 'csharp',
    'cs': 'csharp',
    'javascript': 'javascript',
    'js': 'javascript',
    'node': 'javascript',
    'nodejs': 'javascript',
    'typescript': 'typescript',
    'ts': 'typescript',
    'visual basic': 'visual_basic',
    'visualbasic': 'visual_basic',
    'vb': 'visual_basic',
    'sql': 'sql',
    'r': 'r',
    'delphi': 'pascal',
    'object pascal': 'pascal',
    'delphi object pascal': 'pascal',
    'pascal': 'pascal',
    'perl': 'perl',
    'pl': 'perl',
    'scratch': 'scratch',
    'sb3': 'scratch',
    'fortran': 'fortran',
    'rust': 'rust',
    'rs': 'rust',
    'matlab': 'matlab',
    'go': 'go',
    'golang': 'go',
    'assembly': 'assembly',
    'asm': 'assembly',
    'nasm': 'assembly',
    'php': 'php',
    'ada': 'ada',
    'swift': 'swift',
    'prolog': 'prolog',
    'kotlin': 'kotlin',
    'classic visual basic': 'classic_visual_basic',
    'classicvisualbasic': 'classic_visual_basic',
    'freebasic': 'classic_visual_basic',
    'free basic': 'classic_visual_basic',
    'cobol': 'cobol',
    'dart': 'dart',
    'ruby': 'ruby',
    'rb': 'ruby',
    'lua': 'lua',
    'bash': 'bash',
    'shell': 'bash',
    'sh': 'bash',
    'powershell': 'powershell',
    'pwsh': 'powershell',
    'binary': 'binary',
    'bin': 'binary',
    'executable': 'binary',
}

LANGUAGE_LABELS = {
    'python': 'Python',
    'c': 'C',
    'cpp': 'C++',
    'java': 'Java',
    'csharp': 'C#',
    'javascript': 'JavaScript',
    'typescript': 'TypeScript',
    'visual_basic': 'Visual Basic',
    'sql': 'SQL',
    'r': 'R',
    'pascal': 'Delphi/Object Pascal',
    'perl': 'Perl',
    'scratch': 'Scratch',
    'fortran': 'Fortran',
    'rust': 'Rust',
    'matlab': 'MATLAB',
    'go': 'Go',
    'assembly': 'Assembly',
    'php': 'PHP',
    'ada': 'Ada',
    'swift': 'Swift',
    'prolog': 'Prolog',
    'kotlin': 'Kotlin',
    'classic_visual_basic': 'Classic Visual Basic',
    'cobol': 'COBOL',
    'dart': 'Dart',
    'ruby': 'Ruby',
    'lua': 'Lua',
    'bash': 'Bash',
    'powershell': 'PowerShell',
    'binary': 'Binary',
}

EXTENSION_LANGUAGE_MAP = {
    '.py': 'python',
    '.c': 'c',
    '.cpp': 'cpp',
    '.cc': 'cpp',
    '.cxx': 'cpp',
    '.java': 'java',
    '.cs': 'csharp',
    '.js': 'javascript',
    '.ts': 'typescript',
    '.vb': 'visual_basic',
    '.sql': 'sql',
    '.r': 'r',
    '.pas': 'pascal',
    '.pl': 'perl',
    '.sb3': 'scratch',
    '.f': 'fortran',
    '.for': 'fortran',
    '.f77': 'fortran',
    '.f90': 'fortran',
    '.f95': 'fortran',
    '.f03': 'fortran',
    '.f08': 'fortran',
    '.rs': 'rust',
    '.m': 'matlab',
    '.go': 'go',
    '.asm': 'assembly',
    '.php': 'php',
    '.adb': 'ada',
    '.ada': 'ada',
    '.swift': 'swift',
    '.pro': 'prolog',
    '.prolog': 'prolog',
    '.plg': 'prolog',
    '.kt': 'kotlin',
    '.bas': 'classic_visual_basic',
    '.cob': 'cobol',
    '.cbl': 'cobol',
    '.dart': 'dart',
    '.rb': 'ruby',
    '.lua': 'lua',
    '.sh': 'bash',
    '.ps1': 'powershell',
    '': 'binary',
    '.exe': 'binary',
}


def getExtraArgs(args: ap.Namespace) -> list[str]:
    return list(getattr(args, 'programArgs', []))


def native_run_cmd(outputfile: str) -> list[str]:
    if c.osName != 'windows' and os.path.isabs(outputfile):
        return [outputfile]

    if c.osName == 'windows':
        return [outputfile]

    return [f'./{outputfile}']


def mono_run_cmd(outputfile: str) -> list[str]:
    if c.osName == 'windows':
        return [outputfile]

    if os.path.isabs(outputfile):
        return [outputfile]

    return [c.MONO_PATH, outputfile]


def matlab_run_cmd(full_path: str, extra_args: list[str]) -> list[str]:
    escaped = full_path.replace("'", "''")
    return [c.MATLAB_PATH, *extra_args, '-batch', f"run('{escaped}')"]


def get_interpret_map(full_path: str, extra_args: list[str], args: ap.Namespace) -> dict[str, tuple[list[str], str]]:
    return {
        'javascript': (apply_tool_override([c.NODE_PATH, *extra_args, full_path], args), 'node'),
        'typescript': (apply_tool_override([c.TS_NODE_PATH, *extra_args, full_path], args), 'ts-node'),
        'ruby': (apply_tool_override([c.RUBY_PATH, *extra_args, full_path], args), 'ruby'),
        'php': (apply_tool_override([c.PHP_PATH, *extra_args, full_path], args), 'php'),
        'lua': (apply_tool_override([c.LUA_PATH, *extra_args, full_path], args), 'lua'),
        'bash': (apply_tool_override([c.BASH_PATH, *extra_args, full_path], args), 'bash'),
        'powershell': (apply_tool_override([c.PWSH_PATH, *extra_args, '-File', full_path], args), 'pwsh'),
        'perl': (apply_tool_override([c.PERL_PATH, *extra_args, full_path], args), 'perl'),
        'r': (apply_tool_override([c.RSCRIPT_PATH, *extra_args, full_path], args), 'Rscript'),
        'scratch': (apply_tool_override([c.TURBOWARP_PATH, *extra_args, 'run', full_path], args), 'twcli'),
        'matlab': (apply_tool_override(matlab_run_cmd(full_path, extra_args), args), 'matlab'),
        'prolog': (apply_tool_override([c.SWIPL_PATH, *extra_args, '-q', '-s', full_path, '-t', 'halt'], args), 'swipl'),
        'dart': (apply_tool_override([c.DART_PATH, *extra_args, full_path], args), 'dart'),
    }


def get_compile_map() -> dict[str, object]:
    return {
        'c': cexec.Executor,
        'cpp': cppexec.Executor,
        'rust': rustexec.Executor,
        'go': goexec.Executor,
        'java': javaexec.Executor,
        'assembly': asmexec.Executor,
    }


def get_command_compile_map(full_path: str, outputfile: str, extra_args: list[str], args: ap.Namespace) -> dict[str, tuple[list[str], list[str], str]]:
    exe_output = outputfile if outputfile.endswith('.exe') else f'{outputfile}.exe'
    jar_output = outputfile if outputfile.endswith('.jar') else f'{outputfile}.jar'

    return {
        'csharp': (
            apply_tool_override([c.CSC_PATH, *extra_args, '-nologo', f'-out:{exe_output}', full_path], args),
            mono_run_cmd(exe_output),
            'C#',
        ),
        'visual_basic': (
            apply_tool_override([c.VBC_PATH, *extra_args, '-nologo', f'-out:{exe_output}', full_path], args),
            mono_run_cmd(exe_output),
            'Visual Basic',
        ),
        'pascal': (
            apply_tool_override([c.FPC_PATH, *extra_args, f'-o{outputfile}', full_path], args),
            native_run_cmd(outputfile),
            'Free Pascal',
        ),
        'fortran': (
            apply_tool_override([c.GFORTRAN_PATH, *extra_args, full_path, '-o', outputfile], args),
            native_run_cmd(outputfile),
            'gfortran',
        ),
        'ada': (
            apply_tool_override([c.GNATMAKE_PATH, *extra_args, full_path, '-o', outputfile], args),
            native_run_cmd(outputfile),
            'gnatmake',
        ),
        'swift': (
            apply_tool_override([c.SWIFTC_PATH, *extra_args, full_path, '-o', outputfile], args),
            native_run_cmd(outputfile),
            'swiftc',
        ),
        'kotlin': (
            apply_tool_override([c.KOTLINC_PATH, *extra_args, full_path, '-include-runtime', '-d', jar_output], args),
            [c.JAVA_PATH, '-jar', jar_output],
            'kotlinc',
        ),
        'classic_visual_basic': (
            apply_tool_override([c.FBC_PATH, *extra_args, full_path, '-x', outputfile], args),
            native_run_cmd(outputfile),
            'fbc',
        ),
        'cobol': (
            apply_tool_override([c.COBC_PATH, *extra_args, '-x', '-o', outputfile, full_path], args),
            native_run_cmd(outputfile),
            'cobc',
        ),
    }


def normalize_language(language: str | None) -> str | None:
    if language is None:
        return None

    normalized = str(language).strip().lower().replace('_', ' ').replace('-', ' ')
    if not normalized:
        return None

    return LANGUAGE_ALIASES.get(normalized)


def resolve_language(args: ap.Namespace, ext: str) -> tuple[str | None, str]:
    lang_override = normalize_language(getattr(args, 'lang', None))
    if getattr(args, 'lang', None) and lang_override is None:
        return None, 'override'

    if lang_override:
        return lang_override, 'override'

    return EXTENSION_LANGUAGE_MAP.get(ext), 'extension'


def format_command(cmd: list[str] | None) -> str:
    if not cmd:
        return '-'

    return shlex.join(cmd)


def print_explain(args: ap.Namespace, plan: dict[str, object]) -> None:
    language = str(plan['language'])
    language_source = str(plan['language_source'])
    mode = str(plan['mode'])
    tool_override = get_tool_override(args)
    config_path = getattr(args, 'configPath', None) or 'none'
    outputfile = plan.get('outputfile')

    print(f"{c.Colours.MAGENTA}[MAHKRAB-CLI]{c.Colours.ENDC} Explain")
    print(f"  target: {plan['targetfile']}")
    print(f"  cwd: {os.getcwd()}")
    print(f"  config: {config_path}")
    print(f"  language: {language} ({language_source})")
    print(f"  mode: {mode}")
    if outputfile:
        print(f"  output: {outputfile}")
    if tool_override:
        print(f"  tool override: {shlex.join(tool_override)}")
    elif getattr(args, 'tool', None):
        print(f"  tool override: {getattr(args, 'tool')}")
    print(f"  run on compile: {bool(getattr(args, 'runOnCompile', False))}")
    print(f"  program args: {format_command(list(getattr(args, 'programArgs', [])))}")
    if plan.get('compile_cmd'):
        print(f"  compile command: {format_command(plan['compile_cmd'])}")
    if plan.get('run_cmd'):
        print(f"  run command: {format_command(plan['run_cmd'])}")
    print()


def build_execution_plan(targetfile: str, outputfile: str | None, args: ap.Namespace, runOnCompile: bool) -> dict[str, object] | None:
    full_path = os.path.abspath(targetfile)
    ext = os.path.splitext(targetfile)[1].lower()
    extra_args = getExtraArgs(args)
    build_dir = getattr(args, 'buildDir', 'build')

    if not outputfile:
        filename = os.path.splitext(os.path.basename(targetfile))[0]
        outputfile = os.path.join(build_dir, filename)

    language_key, language_source = resolve_language(args, ext)
    if language_key is None:
        requested = getattr(args, 'lang', None)
        if requested:
            print(
                f"{c.Colours.MAGENTA}[MAHKRAB-CLI] -{c.Colours.ENDC} "
                f"{c.Colours.RED}Error:{c.Colours.ENDC} Unsupported language override: {requested}"
            )
        else:
            print(
                f"{c.Colours.MAGENTA}[MAHKRAB-CLI] -{c.Colours.ENDC} "
                f"{c.Colours.RED}Error:{c.Colours.ENDC} Unsupported file type: {ext or '[no extension]'}"
            )
        return None

    interpret_map = get_interpret_map(full_path, extra_args, args)
    compile_map = get_compile_map()
    command_compile_map = get_command_compile_map(full_path, outputfile, extra_args, args)

    if language_key == 'python':
        tool_override = get_tool_override(args)
        python_cmd = str(getattr(args, 'pythonCmd', c.PYTHON_PATH))
        return {
            'kind': 'python',
            'language_key': language_key,
            'language': LANGUAGE_LABELS[language_key],
            'language_source': language_source,
            'mode': 'interpreted',
            'targetfile': full_path,
            'outputfile': None,
            'compile_cmd': None,
            'run_cmd': [*tool_override, '-u', *extra_args, full_path] if tool_override else [python_cmd, '-u', *extra_args, full_path],
        }

    if language_key in compile_map:
        compile_cmd = None
        run_cmd = None
        if language_key == 'c':
            compile_cmd = apply_tool_override([c.GCC_PATH, full_path, *cexec.Executor.findFlags(full_path), *extra_args, '-o', outputfile], args)
            run_cmd = native_run_cmd(outputfile)
        elif language_key == 'cpp':
            compile_cmd = apply_tool_override([c.GPP_PATH, full_path, *cppexec.Executor.findFlags(full_path), *extra_args, '-o', outputfile], args)
            run_cmd = native_run_cmd(outputfile)
        elif language_key == 'rust':
            compile_cmd = apply_tool_override([c.RUSTC_PATH, full_path, *extra_args, '-o', outputfile], args)
            run_cmd = native_run_cmd(outputfile)
        elif language_key == 'go':
            compile_cmd = apply_tool_override([c.GO_PATH, 'build', *extra_args, '-o', outputfile, full_path], args)
            run_cmd = native_run_cmd(outputfile)
        elif language_key == 'java':
            classname = os.path.splitext(os.path.basename(full_path))[0]
            out_dir = os.path.dirname(outputfile) or 'build'
            compile_cmd = apply_tool_override([c.JAVAC_PATH, *extra_args, '-d', out_dir, full_path], args)
            run_cmd = [c.JAVA_PATH, '-cp', out_dir, classname]
        elif language_key == 'assembly':
            objfile = f'{outputfile}.o'
            compile_cmd = apply_tool_override([c.NASM_PATH, *extra_args, '-f', 'elf64', full_path, '-o', objfile], args)
            run_cmd = native_run_cmd(outputfile)

        return {
            'kind': 'compiled_executor',
            'language_key': language_key,
            'language': LANGUAGE_LABELS[language_key],
            'language_source': language_source,
            'mode': 'compile+run' if runOnCompile else 'compile',
            'targetfile': full_path,
            'outputfile': outputfile,
            'compile_cmd': compile_cmd,
            'run_cmd': run_cmd if runOnCompile else None,
            'executor': compile_map[language_key],
        }

    if language_key in command_compile_map:
        cmd, run_cmd, _tool_name = command_compile_map[language_key]
        return {
            'kind': 'command_compile',
            'language_key': language_key,
            'language': LANGUAGE_LABELS[language_key],
            'language_source': language_source,
            'mode': 'compile+run' if runOnCompile else 'compile',
            'targetfile': full_path,
            'outputfile': outputfile,
            'compile_cmd': cmd,
            'run_cmd': run_cmd if runOnCompile else None,
            'tool_name': _tool_name,
        }

    if language_key == 'sql':
        tool_override = get_tool_override(args)
        sqlite_cmd = c.SQLITE3_PATH
        return {
            'kind': 'sql',
            'language_key': language_key,
            'language': LANGUAGE_LABELS[language_key],
            'language_source': language_source,
            'mode': 'interpreted',
            'targetfile': full_path,
            'outputfile': None,
            'compile_cmd': None,
            'run_cmd': [*tool_override, *extra_args, ':memory:'] if tool_override else [sqlite_cmd, *extra_args, ':memory:'],
        }

    if language_key in interpret_map:
        run_cmd, tool_name = interpret_map[language_key]
        return {
            'kind': 'interpreted',
            'language_key': language_key,
            'language': LANGUAGE_LABELS[language_key],
            'language_source': language_source,
            'mode': 'interpreted',
            'targetfile': full_path,
            'outputfile': None,
            'compile_cmd': None,
            'run_cmd': run_cmd,
            'tool_name': tool_name,
        }

    if language_key == 'binary':
        run_path = binexec.resolve_binary_path(targetfile, build_dir)
        if c.osName == 'windows':
            run_cmd = [run_path]
        elif os.path.isabs(run_path):
            run_cmd = [run_path]
        else:
            run_cmd = [f'./{run_path}']

        run_cmd.extend(extra_args)

        return {
            'kind': 'binary',
            'language_key': language_key,
            'language': LANGUAGE_LABELS[language_key],
            'language_source': language_source,
            'mode': 'run',
            'targetfile': full_path,
            'outputfile': None,
            'compile_cmd': None,
            'run_cmd': run_cmd,
        }

    print(
        f"{c.Colours.MAGENTA}[MAHKRAB-CLI] -{c.Colours.ENDC} "
        f"{c.Colours.RED}Error:{c.Colours.ENDC} No executor available for {LANGUAGE_LABELS.get(language_key, language_key)}."
    )
    return None


def run(targetfile: str, outputfile: str | None, args: ap.Namespace, runOnCompile: bool) -> None:
    if not targetfile:
        print(
            f"{c.Colours.MAGENTA}[MAHKRAB-CLI] -{c.Colours.ENDC} "
            f"{c.Colours.RED}Error:{c.Colours.ENDC} No target file specified."
        )
        return

    plan = build_execution_plan(targetfile, outputfile, args, runOnCompile)
    if plan is None:
        return

    if getattr(args, 'explain', False):
        print_explain(args, plan)

    kind = plan['kind']
    full_path = str(plan['targetfile'])

    if kind == 'python':
        pyexec.Executor.exec(full_path, str(outputfile or ''), args)
    elif kind == 'compiled_executor':
        plan['executor'].exec(full_path, str(plan['outputfile']), args, runOnCompile)
    elif kind == 'command_compile':
        cmdexec.Executor.exec(
            list(plan['compile_cmd']),
            list(plan['run_cmd'] or []),
            str(plan['tool_name']),
            runOnCompile,
        )
    elif kind == 'sql':
        sqlexec.Executor.exec(full_path, str(outputfile or ''), args)
    elif kind == 'interpreted':
        interpexec.Executor.exec(list(plan['run_cmd']), str(plan['tool_name']), args)
    elif kind == 'binary':
        binexec.execbin(targetfile, getattr(args, 'buildDir', 'build'), getExtraArgs(args))
