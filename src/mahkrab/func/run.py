import os
import argparse as ap

from mahkrab import constants as c
from mahkrab.func.executors.compiled import (
    cexec, binexec, asmexec, cppexec, 
    rustexec, goexec, javaexec
)
from mahkrab.func.executors.interpreted import (
    pyexec, interpexec
)

def run(targetfile: str, outputfile: str, args: ap.Namespace, runOnCompile: bool) -> None:
    if not targetfile:
        print(
            f"{c.Colours.MAGENTA}[MAHKRAB-CLI] -{c.Colours.ENDC} "
            f"{c.Colours.RED}Error:{c.Colours.ENDC} No target file specified."
        )
        return
    
    full_path = os.path.abspath(targetfile)         
    
    ext = os.path.splitext(targetfile)[1].lower()
    
    inerpret_map = {
        '.js': (c.NODE_PATH, 'node'),
        '.ts': (c.TS_NODE_PATH, 'ts-node'),
        '.rb': (c.RUBY_PATH, 'ruby'),
        '.php': (c.PHP_PATH, 'php'),
        '.lua': (c.LUA_PATH, 'lua'),
        '.sh': (c.BASH_PATH, 'bash'),
        '.ps1': (c.PWSH_PATH, 'pwsh'),
        '.pl': (c.PERL_PATH, 'perl'),
    }
    
    compile_map = {
        '.c': cexec.Executor,
        '.cpp': cppexec.Executor,
        '.cc': cppexec.Executor,
        '.cxx': cppexec.Executor,
        '.rs': rustexec.Executor,
        '.go': goexec.Executor,
        '.java': javaexec.Executor,
        '.asm': asmexec.Executor,
    }
    
    if ext == '.py':
        pyexec.Executor.exec(targetfile, outputfile, args)
    elif ext in compile_map:
        compile_map[ext].exec(full_path, outputfile, args, runOnCompile)
    elif ext in inerpret_map:
        interpreter, tool_name = inerpret_map[ext]
        if ext == '.ps1':
            run_cmd = [interpreter, '-File', full_path]
        else:
            run_cmd = [interpreter, full_path]
        interpexec.Executor.exec(run_cmd, tool_name, args)
    else:
        if ext in ("", ".exe"):
            binexec.execbin(targetfile)
