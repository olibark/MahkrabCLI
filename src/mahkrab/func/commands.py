from __future__ import annotations

import argparse as ap
import os

from mahkrab import constants as c
from mahkrab.func.executors.compiled import (
    asmexec,
    cexec,
    cppexec,
    goexec,
    javaexec,
    rustexec,
)
from mahkrab.tools.tooloverride import apply_tool_override


def getCompileArgs(args: ap.Namespace) -> list[str]:
    return list(getattr(args, 'compileArgs', []))


def getProgramArgs(args: ap.Namespace) -> list[str]:
    return list(getattr(args, 'programArgs', []))


def native_run_cmd(outputfile: str, program_args: list[str] | None = None) -> list[str]:
    if c.osName != 'windows' and os.path.isabs(outputfile):
        run_cmd = [outputfile]
    elif c.osName == 'windows':
        run_cmd = [outputfile]
    else:
        run_cmd = [f'./{outputfile}']

    if program_args:
        run_cmd.extend(program_args)

    return run_cmd


def mono_run_cmd(outputfile: str, program_args: list[str] | None = None) -> list[str]:
    if c.osName == 'windows':
        run_cmd = [outputfile]
    elif os.path.isabs(outputfile):
        run_cmd = [outputfile]
    else:
        run_cmd = [c.MONO_PATH, outputfile]

    if program_args:
        run_cmd.extend(program_args)

    return run_cmd


def matlab_run_cmd(full_path: str, compile_args: list[str]) -> list[str]:
    escaped = full_path.replace("'", "''")
    return [c.MATLAB_PATH, *compile_args, '-batch', f"run('{escaped}')"]


def prolog_run_cmd(full_path: str, compile_args: list[str], program_args: list[str]) -> list[str]:
    run_cmd = [c.SWIPL_PATH, *compile_args, '-q', '-s', full_path, '-t', 'halt']
    if program_args:
        run_cmd.extend(['--', *program_args])

    return run_cmd


def get_interpret_map(
        full_path: str,
        compile_args: list[str],
        program_args: list[str],
        args: ap.Namespace,
    ) -> dict[str, tuple[list[str], str]]:

    return {
        'javascript': (apply_tool_override([c.NODE_PATH, *compile_args, full_path, *program_args], args), 'node'),
        'typescript': (apply_tool_override([c.TS_NODE_PATH, *compile_args, full_path, *program_args], args), 'ts-node'),
        'ruby': (apply_tool_override([c.RUBY_PATH, *compile_args, full_path, *program_args], args), 'ruby'),
        'php': (apply_tool_override([c.PHP_PATH, *compile_args, full_path, *program_args], args), 'php'),
        'lua': (apply_tool_override([c.LUA_PATH, *compile_args, full_path, *program_args], args), 'lua'),
        'bash': (apply_tool_override([c.BASH_PATH, *compile_args, full_path, *program_args], args), 'bash'),
        'powershell': (apply_tool_override([c.PWSH_PATH, *compile_args, '-File', full_path, *program_args], args), 'pwsh'),
        'perl': (apply_tool_override([c.PERL_PATH, *compile_args, full_path, *program_args], args), 'perl'),
        'r': (apply_tool_override([c.RSCRIPT_PATH, *compile_args, full_path, *program_args], args), 'Rscript'),
        'scratch': (apply_tool_override([c.TURBOWARP_PATH, *compile_args, 'run', full_path], args), 'twcli'),
        'matlab': (apply_tool_override(matlab_run_cmd(full_path, compile_args), args), 'matlab'),
        'prolog': (apply_tool_override(prolog_run_cmd(full_path, compile_args, program_args), args), 'swipl'),
        'dart': (apply_tool_override([c.DART_PATH, *compile_args, full_path, *program_args], args), 'dart'),
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


def get_command_compile_map(
        full_path: str,
        outputfile: str,
        compile_args: list[str],
        program_args: list[str],
        args: ap.Namespace,
    ) -> dict[str, tuple[list[str], list[str], str]]:

    exe_output = outputfile if outputfile.endswith('.exe') else f'{outputfile}.exe'
    jar_output = outputfile if outputfile.endswith('.jar') else f'{outputfile}.jar'

    return {
        'csharp': (
            apply_tool_override([c.CSC_PATH, *compile_args, '-nologo', f'-out:{exe_output}', full_path], args),
            mono_run_cmd(exe_output, program_args),
            'C#',
        ),
        'visual_basic': (
            apply_tool_override([c.VBC_PATH, *compile_args, '-nologo', f'-out:{exe_output}', full_path], args),
            mono_run_cmd(exe_output, program_args),
            'Visual Basic',
        ),
        'pascal': (
            apply_tool_override([c.FPC_PATH, *compile_args, f'-o{outputfile}', full_path], args),
            native_run_cmd(outputfile, program_args),
            'Free Pascal',
        ),
        'fortran': (
            apply_tool_override([c.GFORTRAN_PATH, *compile_args, full_path, '-o', outputfile], args),
            native_run_cmd(outputfile, program_args),
            'gfortran',
        ),
        'ada': (
            apply_tool_override([c.GNATMAKE_PATH, *compile_args, full_path, '-o', outputfile], args),
            native_run_cmd(outputfile, program_args),
            'gnatmake',
        ),
        'swift': (
            apply_tool_override([c.SWIFTC_PATH, *compile_args, full_path, '-o', outputfile], args),
            native_run_cmd(outputfile, program_args),
            'swiftc',
        ),
        'kotlin': (
            apply_tool_override([c.KOTLINC_PATH, *compile_args, full_path, '-include-runtime', '-d', jar_output], args),
            [c.JAVA_PATH, '-jar', jar_output, *program_args],
            'kotlinc',
        ),
        'classic_visual_basic': (
            apply_tool_override([c.FBC_PATH, *compile_args, full_path, '-x', outputfile], args),
            native_run_cmd(outputfile, program_args),
            'fbc',
        ),
        'cobol': (
            apply_tool_override([c.COBC_PATH, *compile_args, '-x', '-o', outputfile, full_path], args),
            native_run_cmd(outputfile, program_args),
            'cobc',
        ),
    }
