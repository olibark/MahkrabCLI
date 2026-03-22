import os
import argparse as ap

from mahkrab import constants as c
from mahkrab.func.executors.compiled import (
    cexec, binexec, asmexec, cppexec,
    rustexec, goexec, javaexec, cmdexec
)
from mahkrab.func.executors.interpreted import (
    pyexec, interpexec, sqlexec
)

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

def native_run_cmd(outputfile: str) -> list[str]:
    if c.osName == 'windows':
        return [outputfile]

    return [f'./{outputfile}']

def mono_run_cmd(outputfile: str) -> list[str]:
    if c.osName == 'windows':
        return [outputfile]

    return [c.MONO_PATH, outputfile]

def matlab_run_cmd(full_path: str) -> list[str]:
    escaped = full_path.replace("'", "''")

    return [c.MATLAB_PATH, '-batch', f"run('{escaped}')"]

def get_interpret_map(full_path: str) -> dict[str, tuple[list[str], str]]:
    return {
        '.js': ([c.NODE_PATH, full_path], 'node'),
        '.ts': ([c.TS_NODE_PATH, full_path], 'ts-node'),
        '.rb': ([c.RUBY_PATH, full_path], 'ruby'),
        '.php': ([c.PHP_PATH, full_path], 'php'),
        '.lua': ([c.LUA_PATH, full_path], 'lua'),
        '.sh': ([c.BASH_PATH, full_path], 'bash'),
        '.ps1': ([c.PWSH_PATH, '-File', full_path], 'pwsh'),
        '.pl': ([c.PERL_PATH, full_path], 'perl'),
        '.r': ([c.RSCRIPT_PATH, full_path], 'Rscript'),
        '.sb3': ([c.TURBOWARP_PATH, 'run', full_path], 'twcli'),
        '.m': (matlab_run_cmd(full_path), 'matlab'),
        '.pro': ([c.SWIPL_PATH, '-q', '-s', full_path, '-t', 'halt'], 'swipl'),
        '.prolog': ([c.SWIPL_PATH, '-q', '-s', full_path, '-t', 'halt'], 'swipl'),
        '.plg': ([c.SWIPL_PATH, '-q', '-s', full_path, '-t', 'halt'], 'swipl'),
        '.dart': ([c.DART_PATH, full_path], 'dart'),
    }

def get_compile_map() -> dict[str, object]:
    return {
        '.c': cexec.Executor,
        '.cpp': cppexec.Executor,
        '.cc': cppexec.Executor,
        '.cxx': cppexec.Executor,
        '.rs': rustexec.Executor,
        '.go': goexec.Executor,
        '.java': javaexec.Executor,
        '.asm': asmexec.Executor,
    }

def get_command_compile_map(full_path: str, outputfile: str) -> dict[str, tuple[list[str], list[str], str]]:
    exe_output = outputfile if outputfile.endswith('.exe') else f'{outputfile}.exe'
    jar_output = outputfile if outputfile.endswith('.jar') else f'{outputfile}.jar'

    return {
        '.cs': ([c.CSC_PATH, '-nologo', f'-out:{exe_output}', full_path], mono_run_cmd(exe_output), 'C#'),
        '.vb': ([c.VBC_PATH, '-nologo', f'-out:{exe_output}', full_path], mono_run_cmd(exe_output), 'Visual Basic'),
        '.pas': ([c.FPC_PATH, f'-o{outputfile}', full_path], native_run_cmd(outputfile), 'Free Pascal'),
        '.f': ([c.GFORTRAN_PATH, full_path, '-o', outputfile], native_run_cmd(outputfile), 'gfortran'),
        '.for': ([c.GFORTRAN_PATH, full_path, '-o', outputfile], native_run_cmd(outputfile), 'gfortran'),
        '.f77': ([c.GFORTRAN_PATH, full_path, '-o', outputfile], native_run_cmd(outputfile), 'gfortran'),
        '.f90': ([c.GFORTRAN_PATH, full_path, '-o', outputfile], native_run_cmd(outputfile), 'gfortran'),
        '.f95': ([c.GFORTRAN_PATH, full_path, '-o', outputfile], native_run_cmd(outputfile), 'gfortran'),
        '.f03': ([c.GFORTRAN_PATH, full_path, '-o', outputfile], native_run_cmd(outputfile), 'gfortran'),
        '.f08': ([c.GFORTRAN_PATH, full_path, '-o', outputfile], native_run_cmd(outputfile), 'gfortran'),
        '.adb': ([c.GNATMAKE_PATH, full_path, '-o', outputfile], native_run_cmd(outputfile), 'gnatmake'),
        '.ada': ([c.GNATMAKE_PATH, full_path, '-o', outputfile], native_run_cmd(outputfile), 'gnatmake'),
        '.swift': ([c.SWIFTC_PATH, full_path, '-o', outputfile], native_run_cmd(outputfile), 'swiftc'),
        '.kt': ([c.KOTLINC_PATH, full_path, '-include-runtime', '-d', jar_output], [c.JAVA_PATH, '-jar', jar_output], 'kotlinc'),
        '.bas': ([c.FBC_PATH, full_path, '-x', outputfile], native_run_cmd(outputfile), 'fbc'),
        '.cob': ([c.COBC_PATH, '-x', '-o', outputfile, full_path], native_run_cmd(outputfile), 'cobc'),
        '.cbl': ([c.COBC_PATH, '-x', '-o', outputfile, full_path], native_run_cmd(outputfile), 'cobc'),
    }

def run(targetfile: str, outputfile: str, args: ap.Namespace, runOnCompile: bool) -> None:
    if not targetfile:
        print(
            f"{c.Colours.MAGENTA}[MAHKRAB-CLI] -{c.Colours.ENDC} "
            f"{c.Colours.RED}Error:{c.Colours.ENDC} No target file specified."
        )
        return

    full_path = os.path.abspath(targetfile)
    ext = os.path.splitext(targetfile)[1].lower()
    interpret_map = get_interpret_map(full_path)
    compile_map = get_compile_map()
    command_compile_map = get_command_compile_map(full_path, outputfile)

    if ext == '.py':
        pyexec.Executor.exec(targetfile, outputfile, args)
    elif ext in compile_map:
        compile_map[ext].exec(full_path, outputfile, args, runOnCompile)
    elif ext in command_compile_map:
        cmd, run_cmd, tool_name = command_compile_map[ext]
        cmdexec.Executor.exec(cmd, run_cmd, tool_name, runOnCompile)
    elif ext == '.sql':
        sqlexec.Executor.exec(full_path, outputfile, args)
    elif ext in interpret_map:
        run_cmd, tool_name = interpret_map[ext]
        interpexec.Executor.exec(run_cmd, tool_name, args)
    else:
        if ext in ('', '.exe'):
            binexec.execbin(targetfile)
