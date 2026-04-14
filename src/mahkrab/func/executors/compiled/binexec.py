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

def resolve_binary_path(targetfile: str, buildDir: str) -> str:
    binary_name = os.path.basename(targetfile)
    candidates = [
        os.path.join(buildDir, binary_name),
        os.path.join(buildDir, targetfile) if not os.path.isabs(targetfile) else None,
        targetfile,
    ]
    candidates = [candidate for candidate in candidates if candidate]

    if c.osName == "windows":
        exe_candidates = []
        for candidate in candidates:
            exe_candidates.append(candidate)
            if not candidate.endswith('.exe'):
                exe_candidates.append(f'{candidate}.exe')
        candidates = exe_candidates

    for candidate in candidates:
        if os.path.exists(candidate):
            return candidate

    return candidates[0]

def execbin(targetfile: str, buildDir: str = "build", programArgs: list[str] | None = None) -> None:
    try: 
        extraArgs = programArgs or []
        run_path = resolve_binary_path(targetfile, buildDir)
        
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
