import subprocess, sys

from mahkrab import constants as c
from mahkrab.func.executors import status
from mahkrab.tools.decorators.timers import compiletime, compileruntime

class Executor:
    @staticmethod
    def exec(cmd: list[str], run_cmd: list[str], tool_name: str, runOnCompile: bool) -> int:
        try:
            if runOnCompile:
                Executor.runOnCompile(cmd, run_cmd)
            else:
                Executor.compile(cmd)
            return 0

        except subprocess.CalledProcessError as e:
            return status.commandFailure(e)
        except FileNotFoundError:
            return status.missingTool(f"The {tool_name} compiler was not found.")
        except Exception as e:
            return status.unexpectedFailure(e)

    @staticmethod
    @compiletime
    def compile(cmd: list[str]) -> None:
        subprocess.run(
            cmd,
            check=True,
            stdout=sys.stdout,
            stderr=sys.stderr,
            text=True,
        )

    @staticmethod
    @compileruntime
    def runOnCompile(cmd: list[str], run_cmd: list[str]) -> None:
        subprocess.run(
            cmd,
            check=True,
            stdout=sys.stdout,
            stderr=sys.stderr,
            text=True,
        )

        subprocess.run(
            run_cmd,
            check=True,
            stdout=sys.stdout,
            stderr=sys.stderr,
            text=True,
        )
