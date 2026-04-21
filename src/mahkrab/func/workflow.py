from __future__ import annotations

import argparse as ap
import subprocess

from mahkrab import constants as c
from mahkrab.func import commands, languages, plans
from mahkrab.func.executors.compiled import binexec, cmdexec
from mahkrab.func.executors.interpreted import interpexec, pyexec, sqlexec


build_execution_plan = plans.build_execution_plan
EXTENSION_LANGUAGE_MAP = languages.EXTENSION_LANGUAGE_MAP
format_command = plans.format_command
get_command_compile_map = commands.get_command_compile_map
get_compile_map = commands.get_compile_map
get_interpret_map = commands.get_interpret_map
getCompileArgs = commands.getCompileArgs
getProgramArgs = commands.getProgramArgs
LANGUAGE_ALIASES = languages.LANGUAGE_ALIASES
LANGUAGE_LABELS = languages.LANGUAGE_LABELS
matlab_run_cmd = commands.matlab_run_cmd
mono_run_cmd = commands.mono_run_cmd
native_run_cmd = commands.native_run_cmd
normalize_language = languages.normalize_language
print_explain = plans.print_explain
prolog_run_cmd = commands.prolog_run_cmd
resolve_language = languages.resolve_language
SUPPORTED_LANGUAGES = languages.SUPPORTED_LANGUAGES


def run(targetfile: str, outputfile: str | None, args: ap.Namespace, runOnCompile: bool) -> None:
    if not targetfile:
        print(
            f"{c.Colours.MAGENTA}[MAHKRAB-CLI] -{c.Colours.ENDC} "
            f"{c.Colours.RED}Error:{c.Colours.ENDC} No target file specified."
        )
        return

    plan = plans.build_execution_plan(targetfile, outputfile, args, runOnCompile)
    if plan is None:
        return

    if getattr(args, 'explain', False):
        plans.print_explain(args, plan)

    kind = plan['kind']
    full_path = str(plan['targetfile'])
    setattr(args, 'resolvedLanguage', plan.get('language_key'))

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
        binexec.execbin(targetfile, getattr(args, 'buildDir', None) or 'build', commands.getProgramArgs(args))


def build(targetfile: str, outputfile: str | None, args: ap.Namespace) -> int:
    if not targetfile:
        print(
            f"{c.Colours.MAGENTA}[MAHKRAB-CLI] -{c.Colours.ENDC} "
            f"{c.Colours.RED}Error:{c.Colours.ENDC} No target file specified."
        )
        return 2

    plan = plans.build_execution_plan(targetfile, outputfile, args, False)
    if plan is None:
        return 2

    if getattr(args, 'explain', False):
        plans.print_explain(args, plan)

    compile_cmd = plan.get('compile_cmd')
    if not compile_cmd:
        print(
            f"{c.Colours.MAGENTA}[MAHKRAB-CLI] -{c.Colours.ENDC} "
            f"{c.Colours.RED}Error:{c.Colours.ENDC} No build step available for {plan['language']}."
        )
        return 2

    try:
        if plan['kind'] == 'compiled_executor':
            setattr(args, 'resolvedLanguage', plan.get('language_key'))
            link_cmd = plan.get('link_cmd')
            if link_cmd:
                plan['executor'].compile(list(compile_cmd), list(link_cmd))
            else:
                plan['executor'].compile(list(compile_cmd))
        elif plan['kind'] == 'command_compile':
            cmdexec.Executor.compile(list(compile_cmd))
        else:
            print(
                f"{c.Colours.MAGENTA}[MAHKRAB-CLI] -{c.Colours.ENDC} "
                f"{c.Colours.RED}Error:{c.Colours.ENDC} No build step available for {plan['language']}."
            )
            return 2

    except subprocess.CalledProcessError as e:
        print(
            f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI] -{c.Colours.ENDC} {c.Colours.RED}"
            f"Error:{c.Colours.ENDC} Command failed with return code {c.Colours.RED}{e.returncode}{c.Colours.ENDC}.\n"
        )
        return e.returncode
    except FileNotFoundError:
        print(
            f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI] -{c.Colours.ENDC} {c.Colours.RED}"
            f"Error:{c.Colours.ENDC} Build tool not found in {c.Colours.RED}PATH{c.Colours.ENDC}.\n"
        )
        return 127
    except Exception as e:
        print(
            f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI] -{c.Colours.ENDC} {c.Colours.RED}"
            f"Error:{c.Colours.ENDC} An unexpected error occured {c.Colours.RED}{e}{c.Colours.RED}.\n"
        )
        return 1

    return 0
