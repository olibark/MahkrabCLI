import argparse as ap
import os, constants as c
from tools import parser
from func import pyexec, cexec, terry
    
def run(targetfile: str, outputfile: str, args: ap.Namespace):
    if not targetfile:
        print(f"{c.Colours.RED}Error:{c.Colours.ENDC} No target file specified for the function.")
        return
    
    full_path = os.path.abspath(targetfile)         
    
    if targetfile.endswith('.py'):
        pyexec.exec(targetfile, outputfile, args)
    elif targetfile.endswith('.c'):
        cexec.exec(full_path, outputfile, args)

def main():
    targetfile, outputfile, args = parser.parse_args()
    
    handlers = {
        'terry': terry.terry, 
        'targetfile': lambda: run(targetfile, outputfile, args)
    }      
    
    for arg_name, handler, in handlers.items():
        if getattr(args, arg_name):
            handler()
            break