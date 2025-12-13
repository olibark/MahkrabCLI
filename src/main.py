import os, constants as c
from tools import parser
from func import terry, run
    
def main():
    targetfile, outputfile, args, runOnCompile = parser.parse_args()
    
    if not targetfile and not args.terry and not args.clear: 
        print(f"mk: {c.Colours.RED}Error:{c.Colours.ENDC} No input file.")
        print(f"{c.Colours.CYAN}Use -h or --help for more information.{c.Colours.ENDC}")
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