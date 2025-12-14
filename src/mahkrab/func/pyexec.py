import os, subprocess, sys

from mahkrab import constants as c
from mahkrab.tools.decorators.timed import timed_decorator as timed

class Executor:
    @staticmethod
    @timed
    def run(targetfile) -> None:
        
        subprocess.run(
            [c.PYTHON_PATH, "-u", targetfile],
            check=True, 
            shell=False,
            stdout=sys.stdout,
            stderr=sys.stderr,
            text=True,
        )
        
    @staticmethod
    def exec(targetfile, outputfile, args) -> None:
        full_path = os.path.abspath(targetfile)
        
        try:
            Executor.run(full_path)
            
        except subprocess.CalledProcessError as e:
            print(
                f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI]{c.Colours.ENDC} {c.Colours.RED}"
                f"Error:{c.Colours.ENDC} Command failed with return code {e.returncode}.\n"
            )
        except FileNotFoundError: 
            print(
                f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI]{c.Colours.ENDC} {c.Colours.RED}"
                f"Error:{c.Colours.ENDC} The {c.PYTHON_PATH} interpreter was not found.\n"
            )
        except Exception as e:
            print(
                f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI]{c.Colours.ENDC} {c.Colours.RED}"
                f"Error:{c.Colours.ENDC} An unexpected error occured {e}.\n"
            )