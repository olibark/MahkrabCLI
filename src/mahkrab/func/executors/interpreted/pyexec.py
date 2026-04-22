import os, subprocess, sys, argparse as ap

from mahkrab import constants as c
from mahkrab.func.executors import status
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
    def exec(targetfile: str, outputfile: str, args: ap.Namespace) -> int:
        full_path = os.path.abspath(targetfile)
        toolOverride = get_tool_override(args)
        compileArgs = list(getattr(args, 'compileArgs', []))
        programArgs = list(getattr(args, 'programArgs', []))
        pythonCmd = str(getattr(args, 'pythonCmd', c.PYTHON_PATH))
        run_cmd = [*toolOverride, '-u', *compileArgs, full_path, *programArgs] if toolOverride else [pythonCmd, '-u', *compileArgs, full_path, *programArgs]
        
        try:
            Executor.run(run_cmd)
            return 0
            
        except subprocess.CalledProcessError as e:
            return status.commandFailure(e)
        except FileNotFoundError: 
            return status.missingTool(
                f"The {(toolOverride[0] if toolOverride else pythonCmd)} interpreter was not found."
            )
        except Exception as e:
            return status.unexpectedFailure(e)
