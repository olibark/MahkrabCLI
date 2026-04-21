from __future__ import annotations

import argparse as ap
import os
import shlex

from mahkrab import constants as c
from mahkrab.func import commands, languages
from mahkrab.func.executors.compiled import asmexec, binexec, cexec, cppexec
from mahkrab.tools.tooloverride import apply_tool_override, get_tool_override


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
    print(f"  compile args: {format_command(commands.getCompileArgs(args))}")
    print(f"  program args: {format_command(commands.getProgramArgs(args))}")
    if plan.get('compile_cmd'):
        print(f"  compile command: {format_command(plan['compile_cmd'])}")
    if plan.get('link_cmd'):
        print(f"  link command: {format_command(plan['link_cmd'])}")
    if plan.get('run_cmd'):
        print(f"  run command: {format_command(plan['run_cmd'])}")
    print()


def build_execution_plan(targetfile: str, outputfile: str | None, args: ap.Namespace, runOnCompile: bool) -> dict[str, object] | None:
    full_path = os.path.abspath(targetfile)
    ext = os.path.splitext(targetfile)[1].lower()
    compile_args = commands.getCompileArgs(args)
    program_args = commands.getProgramArgs(args)
    build_dir = getattr(args, 'buildDir', None) or 'build'

    if not outputfile:
        filename = os.path.splitext(os.path.basename(targetfile))[0]
        outputfile = os.path.join(build_dir, filename)

    language_key, language_source = languages.resolve_language(args, ext)
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

    interpret_map = commands.get_interpret_map(full_path, compile_args, program_args, args)
    compile_map = commands.get_compile_map()
    command_compile_map = commands.get_command_compile_map(full_path, outputfile, compile_args, program_args, args)

    if language_key == 'python':
        tool_override = get_tool_override(args)
        python_cmd = str(getattr(args, 'pythonCmd', c.PYTHON_PATH))
        return {
            'kind': 'python',
            'language_key': language_key,
            'language': languages.LANGUAGE_LABELS[language_key],
            'language_source': language_source,
            'mode': 'interpreted',
            'targetfile': full_path,
            'outputfile': None,
            'compile_cmd': None,
            'run_cmd': [*tool_override, '-u', *compile_args, full_path, *program_args] if tool_override else [python_cmd, '-u', *compile_args, full_path, *program_args],
        }

    if language_key in compile_map or asmexec.is_assembly_language(language_key):
        compile_cmd = None
        link_cmd = None
        run_cmd = None
        if language_key == 'c':
            compile_cmd = apply_tool_override([c.GCC_PATH, full_path, *cexec.Executor.findFlags(full_path), *compile_args, '-o', outputfile], args)
            run_cmd = commands.native_run_cmd(outputfile, program_args)
        elif language_key == 'cpp':
            compile_cmd = apply_tool_override([c.GPP_PATH, full_path, *cppexec.Executor.findFlags(full_path), *compile_args, '-o', outputfile], args)
            run_cmd = commands.native_run_cmd(outputfile, program_args)
        elif language_key == 'rust':
            compile_cmd = apply_tool_override([c.RUSTC_PATH, full_path, *compile_args, '-o', outputfile], args)
            run_cmd = commands.native_run_cmd(outputfile, program_args)
        elif language_key == 'go':
            compile_cmd = apply_tool_override([c.GO_PATH, 'build', *compile_args, '-o', outputfile, full_path], args)
            run_cmd = commands.native_run_cmd(outputfile, program_args)
        elif language_key == 'java':
            classname = os.path.splitext(os.path.basename(full_path))[0]
            out_dir = os.path.dirname(outputfile) or 'build'
            compile_cmd = apply_tool_override([c.JAVAC_PATH, *compile_args, '-d', out_dir, full_path], args)
            run_cmd = [c.JAVA_PATH, '-cp', out_dir, classname, *program_args]
        elif asmexec.is_assembly_language(language_key):
            assembly_plan = asmexec.build_plan(full_path, outputfile, args, runOnCompile, language_key)
            if assembly_plan is None:
                return None

            language_key = str(assembly_plan['language_key'])
            compile_cmd = list(assembly_plan['compile_cmd'])
            link_cmd = list(assembly_plan['link_cmd'])
            outputfile = str(assembly_plan['outputfile'])
            run_cmd = list(assembly_plan['run_cmd']) if assembly_plan['run_cmd'] else None

        return {
            'kind': 'compiled_executor',
            'language_key': language_key,
            'language': languages.LANGUAGE_LABELS[language_key],
            'language_source': language_source,
            'mode': 'compile+run' if runOnCompile else 'compile',
            'targetfile': full_path,
            'outputfile': outputfile,
            'compile_cmd': compile_cmd,
            'link_cmd': link_cmd,
            'run_cmd': run_cmd if runOnCompile else None,
            'executor': asmexec.Executor if asmexec.is_assembly_language(language_key) else compile_map[language_key],
        }

    if language_key in command_compile_map:
        cmd, run_cmd, _tool_name = command_compile_map[language_key]
        return {
            'kind': 'command_compile',
            'language_key': language_key,
            'language': languages.LANGUAGE_LABELS[language_key],
            'language_source': language_source,
            'mode': 'compile+run' if runOnCompile else 'compile',
            'targetfile': full_path,
            'outputfile': outputfile,
            'compile_cmd': cmd,
            'link_cmd': None,
            'run_cmd': run_cmd if runOnCompile else None,
            'tool_name': _tool_name,
        }

    if language_key == 'sql':
        tool_override = get_tool_override(args)
        sqlite_cmd = c.SQLITE3_PATH
        return {
            'kind': 'sql',
            'language_key': language_key,
            'language': languages.LANGUAGE_LABELS[language_key],
            'language_source': language_source,
            'mode': 'interpreted',
            'targetfile': full_path,
            'outputfile': None,
            'compile_cmd': None,
            'link_cmd': None,
            'run_cmd': [*tool_override, *compile_args, ':memory:'] if tool_override else [sqlite_cmd, *compile_args, ':memory:'],
        }
        
    if language_key in interpret_map:
        run_cmd, tool_name = interpret_map[language_key]
        return {
            'kind': 'interpreted',
            'language_key': language_key,
            'language': languages.LANGUAGE_LABELS[language_key],
            'language_source': language_source,
            'mode': 'interpreted',
            'targetfile': full_path,
            'outputfile': None,
            'compile_cmd': None,
            'link_cmd': None,
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

        run_cmd.extend(program_args)

        return {
            'kind': 'binary',
            'language_key': language_key,
            'language': languages.LANGUAGE_LABELS[language_key],
            'language_source': language_source,
            'mode': 'run',
            'targetfile': full_path,
            'outputfile': None,
            'compile_cmd': None,
            'link_cmd': None,
            'run_cmd': run_cmd,
        }

    print(
        f"{c.Colours.MAGENTA}[MAHKRAB-CLI] -{c.Colours.ENDC} "
        f"{c.Colours.RED}Error:{c.Colours.ENDC} No executor available for {languages.LANGUAGE_LABELS.get(language_key, language_key)}."
    )
    return None
