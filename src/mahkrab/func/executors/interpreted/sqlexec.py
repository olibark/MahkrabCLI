import subprocess, sys
import argparse as ap

from mahkrab import constants as c
from mahkrab.func.executors import status
from mahkrab.tools.decorators.timers import runtime
from mahkrab.tools.tooloverride import get_tool_override

class Executor:
    @staticmethod
    @runtime
    def run(full_path: str, run_cmd: list[str]) -> None:
        with open(full_path, 'r', encoding='utf-8') as handle:
            subprocess.run(
                run_cmd,
                check=True,
                stdin=handle,
                stdout=sys.stdout,
                stderr=sys.stderr,
                text=True,
            )

    @staticmethod
    def exec(full_path: str, outputfile: str, args: ap.Namespace) -> int:
        compileArgs = list(getattr(args, 'compileArgs', []))
        toolOverride = get_tool_override(args)
        sqliteCmd = toolOverride[0] if toolOverride else c.SQLITE3_PATH
        run_cmd = [*toolOverride, *compileArgs, ':memory:'] if toolOverride else [sqliteCmd, *compileArgs, ':memory:']

        try:
            Executor.run(full_path, run_cmd)
            return 0

        except subprocess.CalledProcessError as e:
            return status.commandFailure(e)
        except FileNotFoundError:
            return status.missingTool(f"The {sqliteCmd} interpreter was not found.")
        except Exception as e:
            return status.unexpectedFailure(e)
