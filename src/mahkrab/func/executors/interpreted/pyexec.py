import os, subprocess, sys, argparse as ap

from mahkrab import constants as c
from mahkrab.tools.decorators.timers import runtime

class Executor:
    @staticmethod
    @runtime
    def run(pythonCmd: str, targetfile: str, programArgs: list[str]) -> None:
        
        subprocess.run(
            [pythonCmd, "-u", *programArgs, targetfile],
            check=True,
            stdout=sys.stdout,
            stderr=sys.stderr,
            text=True,
        )
        
    @staticmethod
    def exec(targetfile: str, outputfile: str, args: ap.Namespace) -> None:
        full_path = os.path.abspath(targetfile)
        pythonCmd = str(getattr(args, 'pythonCmd', c.PYTHON_PATH))
        programArgs = list(getattr(args, 'programArgs', []))
        
        try:
            Executor.run(pythonCmd, full_path, programArgs)
            
        except subprocess.CalledProcessError as e:
            print(
                f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI]{c.Colours.ENDC} {c.Colours.RED}"
                f"Error:{c.Colours.ENDC} Command failed with return code {e.returncode}.\n"
            )
        except FileNotFoundError: 
            print(
                f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI]{c.Colours.ENDC} {c.Colours.RED}"
                f"Error:{c.Colours.ENDC} The {pythonCmd} interpreter was not found.\n"
            )
        except Exception as e:
            print(
                f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI]{c.Colours.ENDC} {c.Colours.RED}"
                f"Error:{c.Colours.ENDC} An unexpected error occured {e}.\n"
            )
