import subprocess, sys
import argparse as ap

from mahkrab import constants as c
from mahkrab.tools.decorators.timers import runtime

class Executor:
    @staticmethod
    @runtime
    def run(run_cmd: list[str]) -> None:
        subprocess.run(
            run_cmd,
            check=True,
            stdout=sys.stdout,
            stderr=sys.stderr,
            text=True,
        )
        
    @staticmethod
    def exec(run_cmd: list[str], tool_name: str, args: ap.Namespace) -> None:
        try:
            Executor.run(run_cmd)
            
        except subprocess.CalledProcessError as e:
            print(
                f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI]{c.Colours.ENDC} {c.Colours.RED}"
                f"Error:{c.Colours.ENDC} Command failed with return code {e.returncode}.\n"
            )
        except FileNotFoundError: 
            print(
                f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI]{c.Colours.ENDC} {c.Colours.RED}"
                f"Error:{c.Colours.ENDC} The {tool_name} interpreter was not found.\n"
            )
        except Exception as e:
            print(
                f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI]{c.Colours.ENDC} {c.Colours.RED}"
                f"Error:{c.Colours.ENDC} An unexpected error occured {e}.\n"
            )
