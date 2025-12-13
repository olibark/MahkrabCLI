import os
import sys
import time
import subprocess

from mahkrab import constants as c

class Executor:
    @staticmethod
    def exec(targetfile, outputfile, args) -> None:
        full_path = os.path.abspath(targetfile)
        
        try:
            starttime = time.time()
            
            subprocess.run(
                [c.PYTHON_PATH, "-u", full_path],
                check=True, 
                shell=False,
                stdout=sys.stdout,
                stderr=sys.stderr,
                text=True,
            )
            
            endtime = time.time()
            timetaken = endtime - starttime
            
            print(
                f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI] -{c.Colours.ENDC} Script executed succesfully"
            )
            print(
                f"{c.Colours.CYAN}Executed in {c.Colours.BLUE}{timetaken:.2f}{c.Colours.CYAN} seconds.{c.Colours.ENDC}\n"
            )
            
        except subprocess.CalledProcessError as e:
            print(
                f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI]{c.Colours.ENDC} {c.Colours.RED}Error:{c.Colours.ENDC} Command failed with return code {e.returncode}.\n"
            )
        except FileNotFoundError: 
            print(
                f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI]{c.Colours.ENDC} {c.Colours.RED}Error:{c.Colours.ENDC} The {c.PYTHON_PATH} interpreter was not found.\n"
            )
        except Exception as e:
            print(
                f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI]{c.Colours.ENDC} {c.Colours.RED}Error:{c.Colours.ENDC} An unexpected error occured {e}.\n"
            )