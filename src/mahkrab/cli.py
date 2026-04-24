import os
import tomllib
from typing import Callable, Optional

from mahkrab import constants as c
from mahkrab.func import configcmd, doctor, og, terry, tree, workflow
from mahkrab.tools import config, initconfig, parser


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

    if args.command == 'init':
        return initconfig.run(args)

    if args.command == 'config':
        return configcmd.run(args)

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
    except ValueError as error:
        printError(str(error))
        return 2

    actionRunTarget = bool(settings.targetfile)
    actionList = bool(args.list)
    actionOgs = bool(args.ogs)
    actionTerry = bool(args.terry)
    actionDoctor = args.command == 'doctor'
    hasAction = actionRunTarget or actionList or actionOgs or actionTerry or actionDoctor

    if args.command in ('build', 'run') and not settings.targetfile:
        printError("No 'entry' configured in .mkconfig/mkconfig.toml.")
        return 2

    if settings.clear and hasAction:
        os.system(c.CLEAR)

    handlers: dict[str, tuple[bool, Callable[[], object]]] = {
        'doctor': (actionDoctor, lambda: doctor.run(settings)),
        'terry': (actionTerry, terry.terry),
        'targetfile': (
            actionRunTarget,
            lambda: (
                workflow.build(settings.targetfile, settings.outputfile, settings)
                if args.command == 'build'
                else workflow.run(
                    settings.targetfile,
                    settings.outputfile,
                    settings,
                    settings.runOnCompile,
                )
            ),
        ),
        'ogs': (actionOgs, og.ogs),
        'list': (actionList, lambda: tree.list(args.list)),
    }

    for _name, (shouldRun, handler) in handlers.items():
        if shouldRun:
            result = handler()
            if _name in ('doctor', 'targetfile') and isinstance(result, int):
                return result

            return 0

    if settings.clear:
        os.system(c.CLEAR)
        return 0

    printNoInputError()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
