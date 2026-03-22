import subprocess, sys
import argparse as ap

from mahkrab import constants as c
from mahkrab.tools.decorators.timers import runtime

class Executor:
    @staticmethod
    @runtime
    def run(full_path: str) -> None:
        with open(full_path, 'r', encoding='utf-8') as handle:
            subprocess.run(
                [c.SQLITE3_PATH, ':memory:'],
                check=True,
                stdin=handle,
                stdout=sys.stdout,
                stderr=sys.stderr,
                text=True,
            )

    @staticmethod
    def exec(full_path: str, outputfile: str, args: ap.Namespace) -> None:
        try:
            Executor.run(full_path)

        except subprocess.CalledProcessError as e:
            print(
                f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI]{c.Colours.ENDC} {c.Colours.RED}"
                f"Error:{c.Colours.ENDC} Command failed with return code {e.returncode}.\n"
            )
        except FileNotFoundError:
            print(
                f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI]{c.Colours.ENDC} {c.Colours.RED}"
                f"Error:{c.Colours.ENDC} The sqlite3 interpreter was not found.\n"
            )
        except Exception as e:
            print(
                f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI]{c.Colours.ENDC} {c.Colours.RED}"
                f"Error:{c.Colours.ENDC} An unexpected error occured {e}.\n"
            )
