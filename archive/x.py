import argparse as ap
import os, constants as c
import subprocess, sys, time

def terry():
    print("1: Thou shall not litter")
    print("2: No gore unless it looks fake.")
    print("3: No pedophilia or child porn.")
    print("4: Dont eat rare meat with blood.")
    print("5: No wife beating.")
    print("6: Do not swing from radio towers with one hand.")
    print("7: Do not disturb")
    
def run(targetfile: str, outputfile: str):
    if not targetfile:
        print("Error: No target file specified for the function.")
        return
    
    full_path = os.path.abspath(targetfile)         
    
    if targetfile.endswith('.py'):
        try:
            startime = time.time()
            subprocess.run(
                f'python3 -u "{full_path}"',
                check=True, 
                shell=True,
                stdout=sys.stdout,
                stderr=sys.stderr,
                text=True
            )   
            endtime = time.time()
            timetaken = endtime - startime
            print(f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI]{c.Colours.ENDC} Script executed succesfully")
            print(f"{c.Colours.CYAN}Executed in {timetaken:.2f} seconds.\n")
            
        except subprocess.CalledProcessError as e:
            print(f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI]{c.Colours.ENDC} {c.Colours.RED}Error:{c.Colours.ENDC} Command failed with return code {e.returncode}.\n")
        except FileNotFoundError: 
            print(f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI]{c.Colours.ENDC} {c.Colours.RED}Error:{c.Colours.ENDC} The 'python3' interpreter was not found.\n")
        except Exception as e:
            print(f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI]{c.Colours.ENDC} {c.Colours.RED}Error:{c.Colours.ENDC} An unexpected error occured {e}.\n")
    
    elif targetfile.endswith('.c'):
        try:
            starttime = time.time()
            subprocess.run(
                f'gcc "{full_path}" -o "{outputfile}"',
                check=True,
                shell=True,
                stdout=sys.stdout,
                stderr=sys.stderr,
                text=True
            )
            endtime = time.time()
            timetaken = endtime - starttime
            print(f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI]{c.Colours.ENDC} Script executed succesfully.")
            print(f"{c.Colours.CYAN}Compiled in {timetaken:.2f} seconds.\n")
            
        except subprocess.CalledProcessError as e:
            print(f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI]{c.Colours.ENDC} {c.Colours.RED}Error:{c.Colours.ENDC} Command failed with return code {e.returncode}.\n")
        except FileNotFoundError: 
            print(f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI]{c.Colours.ENDC} {c.Colours.RED}Error:{c.Colours.ENDC} Gcc not found in PATH.\n")
        except Exception as e:
            print(f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI]{c.Colours.ENDC} {c.Colours.RED}Error:{c.Colours.ENDC} An unexpected error occured {e}.\n")
    
def main():
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

    handlers = {
        'terry': terry, 
        'targetfile': lambda: run(targetfile, outputfile)
    }      
    
    for arg_name, handler, in handlers.items():
        if getattr(args, arg_name):
            handler()
            break
         
main()