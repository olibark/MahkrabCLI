import os
import argparse as ap

from mahkrab.tools.getversion import get_version

def parse_args():
    parser = ap.ArgumentParser(
        prog='MAHKRAB-CLI', 
        description="A script to demonstrate command-line flags."
        )
    parser.add_argument(
        '-o', '--output', 
        type=str, metavar='<file>', 
        help="Name of output file"
    )
    parser.add_argument(
        'targetfile', nargs='?', 
        type=str, help="Pass file to function"
    )
    parser.add_argument(
        '-t', '--terry', 
        action="store_true", 
        help="The commands of Terry the terrible"
    )
    parser.add_argument(
        '-v', '--version', 
        action='version', 
        version=f"mahkrab {get_version()}",
        help="Show program version"
    )
    parser.add_argument(
        '-r', '--run', 
        action='store_true', 
        help="Run the target file after compilation"
    )
    parser.add_argument(
        '-c', '--clear', 
        action='store_true', 
        help="Clear the console before execution"
    )
    parser.add_argument(
        '-ls', '--list', 
        type=int, metavar='<listLevel>', nargs='?', const=1,
        help="Lists the directories contents"
    )
    parser.add_argument(
        '-og','--ogs',
        action='store_true',
        help="ogs"
    )
    
    args = parser.parse_args()
    
    targetfile = None
    outputfile = None
    level = None
    
    if not os.path.exists("build"):
        os.makedirs("build")
    
    if args.targetfile: 
        targetfile = args.targetfile
    if args.output:
        outputfile = args.output
    if args.list: 
        level = args.list
    elif targetfile:
        filename = os.path.splitext(os.path.basename(targetfile))[0]
        outputfile = os.path.join("build", filename)
    else:
        outputfile = None
        
    runOnCompile = bool(args.run)
    
    return targetfile, outputfile, args, runOnCompile, level
