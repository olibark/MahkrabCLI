from __future__ import annotations

import subprocess

from mahkrab import constants as c


def commandFailure(error: subprocess.CalledProcessError) -> int:
    print(
        f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI] -{c.Colours.ENDC} {c.Colours.RED}"
        f"Error:{c.Colours.ENDC} Command failed with return code "
        f"{c.Colours.RED}{error.returncode}{c.Colours.ENDC}.\n"
    )
    return int(error.returncode)


def missingTool(message: str) -> int:
    print(
        f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI] -{c.Colours.ENDC} {c.Colours.RED}"
        f"Error:{c.Colours.ENDC} {message}\n"
    )
    return 127


def unexpectedFailure(error: Exception) -> int:
    print(
        f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI] -{c.Colours.ENDC} {c.Colours.RED}"
        f"Error:{c.Colours.ENDC} An unexpected error occured {c.Colours.RED}{error}{c.Colours.RED}.\n"
    )
    return 1
