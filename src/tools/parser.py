import os, sys, argparse as ap

def parse_args():
    parser = ap.ArgumentParser(
        prog='MAHKRAB-CLI', 
        description="A script to demonstrate command-line flags."
        )
    
    parser.add_argument('-o', '--output', type=str, metavar='<file>', help="Name of output file")
    parser.add_argument('targetfile', nargs='?', type=str, help="Pass file to function")
    parser.add_argument('-t', '--terry', action="store_true", help="The commands of Terry the terrible")
    parser.add_argument('-v', '--version', action='version', version='MAHKRAB-CLI 1.0', help="Show program version")
    parser.add_argument('-r', '--run', action='store_true', help="Run the target file after compilation")
        
    args = parser.parse_args()
    
    targetfile = args.targetfile
    
    if not os.path.exists("build"):
        os.makedirs("build")
    
    if args.output:
        outputfile = args.output
    elif targetfile:
        filename = os.path.splitext(os.path.basename(targetfile))[0]
        outputfile = os.path.join("build", filename)
    else:
        outputfile = None
        
    runOnCompile = False
    if args.run:
        runOnCompile = True
    
    return targetfile, outputfile, args, runOnCompile