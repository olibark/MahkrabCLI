import subprocess, sys
import argparse as ap

from mahkrab import constants as c
from mahkrab.func.executors import status
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
    def exec(run_cmd: list[str], tool_name: str, args: ap.Namespace) -> int:
        try:
            Executor.run(run_cmd)
            return 0
            
        except subprocess.CalledProcessError as e:
            return status.commandFailure(e)
        except FileNotFoundError: 
            return status.missingTool(f"The {tool_name} interpreter was not found.")
        except Exception as e:
            return status.unexpectedFailure(e)
