import os, argparse as ap, constants as c
from func import pyexec, cexec

def run(targetfile: str, outputfile: str, args: ap.Namespace, runOnCompile: bool) -> None:
    #if not targetfile and not 
    if not targetfile:
        print(f"{c.Colours.RED}Error:{c.Colours.ENDC} No target file specified for the function.")
        return
    
    full_path = os.path.abspath(targetfile)         
    
    if targetfile.endswith('.py'):
        pyexec.Executor.exec(targetfile, outputfile, args)
    elif targetfile.endswith('.c'):
        cexec.Executor.exec(full_path, outputfile, args, runOnCompile)
    elif '.' not in targetfile:
        cexec.Executor.runbin(targetfile, args)
        