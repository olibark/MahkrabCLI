import os, subprocess, sys, argparse as ap

from mahkrab import constants as c
from mahkrab.tools.decorators.timers import runtime
from mahkrab.tools.tooloverride import get_tool_override

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
    def exec(targetfile: str, outputfile: str, args: ap.Namespace) -> None:
        full_path = os.path.abspath(targetfile)
        toolOverride = get_tool_override(args)
        programArgs = list(getattr(args, 'programArgs', []))
        pythonCmd = str(getattr(args, 'pythonCmd', c.PYTHON_PATH))
        run_cmd = [*toolOverride, '-u', *programArgs, full_path] if toolOverride else [pythonCmd, '-u', *programArgs, full_path]
        
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
                f"Error:{c.Colours.ENDC} The {(toolOverride[0] if toolOverride else pythonCmd)} interpreter was not found.\n"
            )
        except Exception as e:
            print(
                f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI]{c.Colours.ENDC} {c.Colours.RED}"
                f"Error:{c.Colours.ENDC} An unexpected error occured {e}.\n"
            )
