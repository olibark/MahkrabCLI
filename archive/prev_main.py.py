import os, constants as c
from tools import parser
from func import terry, run
from constants import *

    
def main():
    targetfile, outputfile, args, runOnCompile = parser.parse_args()
    
    if not targetfile and not args.terry and not args.clear: 
        print(f"\n{Colours.MAGENTA}[MAHKRAB-CLI] - {Colours.RED}Error:{Colours.ENDC} No input file.")
        print(f"{Colours.CYAN}Use {Colours.BLUE}-h {Colours.CYAN}or {Colours.BLUE}--help{Colours.CYAN} for more information.{Colours.ENDC}\n")
        return
    
    handlers = {
        'terry': terry.terry, 
        'targetfile': lambda: run.run(targetfile, outputfile, args, runOnCompile),
    }      
    
    for arg_name, handler, in handlers.items():
        if getattr(args, arg_name):
            if args.clear: 
                os.system(c.CLEAR)
            handler()
            break
           
main()