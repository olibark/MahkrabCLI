import subprocess, os, sys

from mahkrab.tools.decorators.timers import runtime
from mahkrab import constants as c 

@runtime
def run(run_cmd: list[str]) -> None:
    subprocess.run(
        run_cmd,
        check=True,
        stdout=sys.stdout,
        stderr=sys.stderr,
        text=True,
    )

def execbin(targetfile: str, programArgs: list[str] | None = None) -> None:
    try: 
        extraArgs = programArgs or []
        build_path = os.path.join("build", targetfile)
        run_path = build_path if os.path.exists(build_path) else targetfile
        
        if c.osName == "windows":
            run_cmd = [run_path]
        elif os.path.isabs(run_path):
            run_cmd = [run_path]
        else:
            run_cmd = [f"./{run_path}"]

        run_cmd.extend(extraArgs)
        
        run(run_cmd)
    
    except subprocess.CalledProcessError as e:
        print(
            f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI] -{c.Colours.ENDC} {c.Colours.RED}"
            f"Error:{c.Colours.ENDC} Command failed with return code {c.Colours.RED}{e.returncode}{c.Colours.ENDC}.\n"
        )
    except FileNotFoundError: 
        print(
            f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI] -{c.Colours.ENDC} {c.Colours.RED}"
            f"Error:{c.Colours.ENDC} Binary not found in {c.Colours.RED}directory{c.Colours.ENDC}.\n"
        )
    except Exception as e:
        print(
            f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI] -{c.Colours.ENDC} {c.Colours.RED}"
            f"Error:{c.Colours.ENDC} An unexpected error occured {c.Colours.RED}{e}{c.Colours.RED}.\n"
        )
