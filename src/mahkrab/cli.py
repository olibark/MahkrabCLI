import os
import tomllib
from typing import Callable, Optional

from mahkrab import constants as c
from mahkrab.func import og, run, terry, tree
from mahkrab.tools import config, parser


def printNoInputError() -> None:
    print(
        f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI] - {c.Colours.RED}Error:{c.Colours.ENDC} No input file."
    )
    print(
        f"{c.Colours.CYAN}Use {c.Colours.BLUE}-h {c.Colours.CYAN}or {c.Colours.BLUE}--help{c.Colours.CYAN} for more information.{c.Colours.ENDC}\n"
    )


def printError(message: str) -> None:
    print(
        f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI] - {c.Colours.RED}Error:{c.Colours.ENDC} {message}\n"
    )


def main(argv: Optional[list[str]] = None) -> int:
    args = parser.parse_args(argv)

    try:
        settings = config.buildSettings(args)
        settings = config.prepareRuntime(settings)
    except FileNotFoundError as error:
        printError(str(error))
        return 2
    except tomllib.TOMLDecodeError as error:
        printError(f'Invalid TOML in config file ({error}).')
        return 2
    except NotADirectoryError as error:
        printError(str(error))
        return 2

    actionRunTarget = bool(settings.targetfile)
    actionList = bool(args.list)
    actionOgs = bool(args.ogs)
    actionTerry = bool(args.terry)
    hasAction = actionRunTarget or actionList or actionOgs or actionTerry

    if args.command == 'run' and not settings.targetfile:
        printError("No 'entry' configured in .mkconfig/.mkconfig.toml.")
        return 2

    if settings.clear and hasAction:
        os.system(c.CLEAR)

    handlers: dict[str, tuple[bool, Callable[[], object]]] = {
        'terry': (actionTerry, terry.terry),
        'targetfile': (
            actionRunTarget,
            lambda: run.run(
                settings.targetfile,
                settings.outputfile,
                settings,
                settings.runOnCompile,
            ),
        ),
        'ogs': (actionOgs, og.ogs),
        'list': (actionList, lambda: tree.list(args.list)),
    }

    for _name, (shouldRun, handler) in handlers.items():
        if shouldRun:
            handler()
            return 0

    if settings.clear:
        os.system(c.CLEAR)
        return 0

    printNoInputError()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
