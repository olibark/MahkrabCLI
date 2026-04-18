import subprocess, sys
import argparse as ap

from mahkrab import constants as c
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
    def exec(full_path: str, outputfile: str, args: ap.Namespace) -> None:
        programArgs = list(getattr(args, 'programArgs', []))
        toolOverride = get_tool_override(args)
        sqliteCmd = toolOverride[0] if toolOverride else c.SQLITE3_PATH
        run_cmd = [*toolOverride, *programArgs, ':memory:'] if toolOverride else [sqliteCmd, *programArgs, ':memory:']

        try:
            Executor.run(full_path, run_cmd)

        except subprocess.CalledProcessError as e:
            print(
                f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI]{c.Colours.ENDC} {c.Colours.RED}"
                f"Error:{c.Colours.ENDC} Command failed with return code {e.returncode}.\n"
            )
        except FileNotFoundError:
            print(
                f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI]{c.Colours.ENDC} {c.Colours.RED}"
                f"Error:{c.Colours.ENDC} The {sqliteCmd} interpreter was not found.\n"
            )
        except Exception as e:
            print(
                f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI]{c.Colours.ENDC} {c.Colours.RED}"
                f"Error:{c.Colours.ENDC} An unexpected error occured {e}.\n"
            )
