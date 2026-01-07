import os
from typing import Callable, Optional

from mahkrab import constants as c 
from mahkrab.tools import parser
from mahkrab.func import terry, run, og, tree

def main(argv: Optional[list[str]] = None) -> int:
    targetfile, outputfile, args, runOnCompile, level = parser.parse_args()
    setattr(args, "targetfile", bool(targetfile))
    
    if not targetfile and not args.terry and not args.clear and not args.ogs and not args.list:
        print(
            f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI] - {c.Colours.RED}Error:{c.Colours.ENDC} No input file."
        )
        print(
            f"{c.Colours.CYAN}Use {c.Colours.BLUE}-h {c.Colours.CYAN}or {c.Colours.BLUE}--help{c.Colours.CYAN} for more information.{c.Colours.ENDC}\n"
        )
        return 2
    
    handlers: dict[str, Callable[[], object]] = {
        'terry': terry.terry,
        'targetfile': lambda: run.run(
            targetfile, outputfile, args, runOnCompile
        ),
        'ogs': og.ogs,
        'list': lambda: tree.list(
            level
        )
    }
    
    for arg_name, handler, in handlers.items():
        if getattr(args, arg_name):
            if args.clear:
                os.system(c.CLEAR)
            handler()
            break
        
    if args.clear and not (args.terry or targetfile):
        os.system(c.CLEAR)

    return 0

if __name__ == "__main__":
    raise SystemExit(main())