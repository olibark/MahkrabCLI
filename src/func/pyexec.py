import time, subprocess, os, sys, constants as c

class Executor:
    def exec(targetfile, outputfile, args):
        full_path = os.path.abspath(targetfile)
        try:
            startime = time.time()
            
            subprocess.run(
                f'{c.PYTHON_PATH} -u "{full_path}"',
                check=True, 
                shell=True,
                stdout=sys.stdout,
                stderr=sys.stderr,
                text=True
            )
            
            endtime = time.time()
            timetaken = endtime - startime
            print(f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI] -{c.Colours.ENDC} Script executed succesfully")
            print(f"{c.Colours.CYAN}Executed in {timetaken:.2f} seconds.\n")
            
        except subprocess.CalledProcessError as e:
            print(f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI]{c.Colours.ENDC} {c.Colours.RED}Error:{c.Colours.ENDC} Command failed with return code {e.returncode}.\n")
        except FileNotFoundError: 
            print(f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI]{c.Colours.ENDC} {c.Colours.RED}Error:{c.Colours.ENDC} The 'python3' interpreter was not found.\n")
        except Exception as e:
            print(f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI]{c.Colours.ENDC} {c.Colours.RED}Error:{c.Colours.ENDC} An unexpected error occured {e}.\n")