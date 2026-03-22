import subprocess, sys

from mahkrab import constants as c
from mahkrab.tools.decorators.timers import compiletime, compileruntime

class Executor:
    @staticmethod
    def exec(cmd: list[str], run_cmd: list[str], tool_name: str, runOnCompile: bool) -> None:
        try:
            if runOnCompile:
                Executor.runOnCompile(cmd, run_cmd)
            else:
                Executor.compile(cmd)

        except subprocess.CalledProcessError as e:
            print(
                f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI]{c.Colours.ENDC} {c.Colours.RED}"
                f"Error:{c.Colours.ENDC} Command failed with return code {e.returncode}.\n"
            )
        except FileNotFoundError:
            print(
                f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI]{c.Colours.ENDC} {c.Colours.RED}"
                f"Error:{c.Colours.ENDC} The {tool_name} compiler was not found.\n"
            )
        except Exception as e:
            print(
                f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI]{c.Colours.ENDC} {c.Colours.RED}"
                f"Error:{c.Colours.ENDC} An unexpected error occured {e}.\n"
            )

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
