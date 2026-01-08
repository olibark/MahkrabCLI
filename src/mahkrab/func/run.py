import os
import argparse as ap

from mahkrab import constants as c
from mahkrab.func import pyexec, cexec, binexec, asmexec

def run(targetfile: str, outputfile: str, args: ap.Namespace, runOnCompile: bool) -> None:
    if not targetfile:
        print(
            f"{c.Colours.MAGENTA}[MAHKRAB-CLI] -{c.Colours.ENDC} "
            f"{c.Colours.RED}Error:{c.Colours.ENDC} No target file specified."
        )
        return
    
    full_path = os.path.abspath(targetfile)         
    
    if targetfile.endswith('.py'):
        pyexec.Executor.exec(targetfile, outputfile, args)
    elif targetfile.endswith('.c'):
        cexec.Executor.exec(full_path, outputfile, args, runOnCompile)
    elif targetfile.endswith('.asm'):
        asmexec.Executor.exec(full_path, outputfile, args, runOnCompile)
    else:
        ext = os.path.splitext(targetfile)[1].lower()
        if ext in ("", ".exe"):
            binexec.execbin(targetfile)
