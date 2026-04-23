import argparse as ap
import shlex
import sys

from mahkrab.tools.targetos import SUPPORTED_TARGET_OSES
from mahkrab.tools.getversion import get_version

COMMANDS = {'build', 'doctor', 'init', 'run'}
SPECIAL_ARG_DESTS = {
    '--compile-args': 'compileArgsRaw',
    '--tool-args': 'compileArgsRaw',
    '--program-args': 'programArgsRaw',
}
OPTION_TOKENS = {
    '-o', '--output',
    '--build-dir',
    '--cwd',
    '--config',
    '--python',
    '--lang',
    '--tool',
    '-r', '--run-on-compile',
    '--compile-args', '--tool-args',
    '--program-args',
    '-q', '--quiet',
    '--verbose',
    '--json',
    '--all',
    '--languages',
    '-c', '--clear',
    '-ls', '--list',
    '-og', '--ogs',
    '-t', '--terry',
    '-e', '--explain',
    '-v', '--version',
    '-h', '--help',
}

def parseArgumentValues(rawArgs: list[list[str]], unknownArgs: list[str] | None = None) -> list[str]:
    args: list[str] = []

    for rawArgGroup in rawArgs:
        for rawArg in rawArgGroup:
            args.extend(shlex.split(rawArg))

    if unknownArgs:
        forwardedArgs = list(unknownArgs)
        if forwardedArgs[0] == '--':
            forwardedArgs = forwardedArgs[1:]

        if forwardedArgs:
            args.extend(forwardedArgs)

    return args


def optionToken(value: str) -> str:
    return value.split('=', 1)[0]


def preprocessArgv(argv: list[str] | None) -> tuple[list[str], dict[str, list[list[str]]]]:
    tokens = list(sys.argv[1:] if argv is None else argv)
    cleanedArgv: list[str] = []
    rawArgValues = {
        'compileArgsRaw': [],
        'programArgsRaw': [],
    }

    index = 0
    while index < len(tokens):
        token = tokens[index]
        tokenKey = optionToken(token)

        if token == '--':
            rawArgValues['programArgsRaw'].append(tokens[index + 1:])
            break

        if tokenKey in SPECIAL_ARG_DESTS:
            dest = SPECIAL_ARG_DESTS[tokenKey]
            group: list[str] = []

            if '=' in token:
                value = token.split('=', 1)[1]
                if value:
                    group.append(value)
                rawArgValues[dest].append(group)
                index += 1
                continue

            index += 1
            if index < len(tokens) and tokens[index] == '--':
                rawArgValues[dest].append(tokens[index + 1:])
                break

            while index < len(tokens) and optionToken(tokens[index]) not in OPTION_TOKENS:
                group.append(tokens[index])
                index += 1

            rawArgValues[dest].append(group)
            continue

        cleanedArgv.append(token)
        index += 1

    return cleanedArgv, rawArgValues

def createParser() -> ap.ArgumentParser:
    return ap.ArgumentParser(
        prog="MAHKRAB-CLI",
        epilog=(
            "Commands: run (compile and run configured entry), "
            "build (compile configured entry only), "
            "init (create project config), "
            "doctor (diagnose external toolchains)."
        ),
    )


def addSharedArgs(parser: ap.ArgumentParser) -> None:
    parser.add_argument(
        '-o', '--output',
        type=str, metavar='<file>',
        help='Output file name',
    )
    parser.add_argument(
        '--build-dir',
        dest='buildDir',
        type=str, metavar='<dir>',
        help='Directory for compiled binaries (default: build)',
    )
    parser.add_argument(
        '--cwd',
        type=str, metavar='<dir>',
        help='Working directory override',
    )
    parser.add_argument(
        '--config',
        type=str, metavar='<file>',
        help='Path to configuration file',
    )
    parser.add_argument(
        '--python',
        dest='pythonCmd',
        type=str, metavar='<python>',
        help='Python interpreter override',
    )
    parser.add_argument(
        '--lang',
        type=str, metavar='<language>',
        help='Language override',
    )
    parser.add_argument(
        '--tool',
        type=str, metavar='<tool>',
        help='Compiler or interpreter override',
    )
    parser.add_argument(
        '-r', '--run-on-compile',
        dest='runOnCompile',
        action='store_true',
        help='Run the target file after compilation',
    )
    parser.add_argument(
        '--compile-args', '--tool-args',
        dest='compileArgsRaw',
        action='append',
        nargs='*',
        default=[],
        metavar='<args>',
        help='Extra compiler/interpreter args (supports quoted values).',
    )
    parser.add_argument(
        '--program-args',
        dest='programArgsRaw',
        action='append',
        nargs='*',
        default=[],
        metavar='<args>',
        help='Args passed to the compiled program or script (supports quoted values).',
    )


def addUtilityArgs(parser: ap.ArgumentParser) -> None:
    parser.add_argument(
        '-c', '--clear',
        action='store_true',
        help="Clear the console before execution"
    )
    parser.add_argument(
        '-ls', '--list',
        type=int, metavar='<listLevel>', nargs='?', const=1,
        help='Lists the directories contents',
    )
    parser.add_argument(
        '-og', '--ogs',
        action='store_true',
        help='ogs',
    )
    parser.add_argument(
        '-t', '--terry',
        action='store_true',
        help='The commands of Terry the terrible',
    )
    parser.add_argument(
        '-e', '--explain',
        action='store_true',
        help='Show resolved settings before execution',
    )
    parser.add_argument(
        '-v', '--version',
        action='version',
        version=f"mahkrab {get_version()}",
        help='Show program version',
    )


def addDoctorArgs(parser: ap.ArgumentParser) -> None:
    doctor_output_group = parser.add_mutually_exclusive_group()
    doctor_output_group.add_argument(
        '-q', '--quiet',
        dest='doctorQuiet',
        action='store_true',
        help='Only print the doctor summary.',
    )
    doctor_output_group.add_argument(
        '--verbose',
        dest='doctorVerbose',
        action='store_true',
        help='Print extra doctor diagnostics, including generated command plans.',
    )
    parser.add_argument(
        '--json',
        dest='doctorJson',
        action='store_true',
        help='Doctor: emit machine-readable JSON output.',
    )
    parser.add_argument(
        '--os',
        dest='targetOs',
        choices=SUPPORTED_TARGET_OSES,
        metavar='<os>',
        help='Doctor: choose install hints for linux, macos, or windows.',
    )
    parser.add_argument(
        '--all',
        dest='doctorAll',
        action='store_true',
        help='Doctor: check every supported language toolchain.',
    )
    parser.add_argument(
        '--languages',
        dest='doctorLanguages',
        action='store_true',
        help='Doctor: list languages available for doctor checks.',
    )


def addInitArgs(parser: ap.ArgumentParser) -> None:
    parser.add_argument(
        'initTarget',
        nargs="?",
        help='Optional entry file for the generated config',
    )
    parser.add_argument(
        '--entry',
        dest='initEntry',
        type=str, metavar='<file>',
        help='Entry file for mk run and mk build',
    )
    parser.add_argument(
        '--lang',
        type=str, metavar='<language>',
        help='Language override written to config',
    )
    parser.add_argument(
        '--os',
        dest='targetOs',
        choices=SUPPORTED_TARGET_OSES,
        metavar='<os>',
        help='Write the target OS for doctor install hints.',
    )
    parser.add_argument(
        '--build-dir',
        dest='buildDir',
        type=str, metavar='<dir>',
        help='Directory for compiled binaries (default: build)',
    )
    parser.add_argument(
        '-o', '--output',
        type=str, metavar='<file>',
        help='Output file name written to config',
    )
    parser.add_argument(
        '-r', '--run-on-compile',
        dest='runOnCompile',
        action='store_true',
        help='Run the target file after compilation',
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Overwrite an existing generated config',
    )


def createDirectParser() -> ap.ArgumentParser:
    parser = createParser()
    parser.add_argument(
        'target',
        nargs="?",
        help='Target file name',
    )
    addSharedArgs(parser)
    addUtilityArgs(parser)
    return parser


def createCommandParser() -> ap.ArgumentParser:
    parser = createParser()
    subparsers = parser.add_subparsers(dest='command')

    runParser = subparsers.add_parser('run', help='Compile and run configured entry')
    addSharedArgs(runParser)
    addUtilityArgs(runParser)

    buildParser = subparsers.add_parser('build', help='Compile configured entry only')
    addSharedArgs(buildParser)
    addUtilityArgs(buildParser)

    initParser = subparsers.add_parser('init', help='Create project config')
    addInitArgs(initParser)

    doctorParser = subparsers.add_parser('doctor', help='Diagnose external toolchains')
    doctorParser.add_argument(
        'doctorTarget',
        nargs="?",
        help='Optional target file or "languages"',
    )
    addSharedArgs(doctorParser)
    addDoctorArgs(doctorParser)
    addUtilityArgs(doctorParser)

    return parser


def fillMissingArgs(args: ap.Namespace) -> None:
    defaults = {
        'target': None,
        'initTarget': None,
        'initEntry': None,
        'doctorTarget': None,
        'targetfile': None,
        'output': None,
        'buildDir': None,
        'cwd': None,
        'config': None,
        'pythonCmd': None,
        'lang': None,
        'targetOs': None,
        'tool': None,
        'runOnCompile': False,
        'compileArgsRaw': [],
        'programArgsRaw': [],
        'compileArgs': [],
        'programArgs': [],
        'doctorQuiet': False,
        'doctorVerbose': False,
        'doctorJson': False,
        'doctorAll': False,
        'doctorLanguages': False,
        'force': False,
        'clear': False,
        'list': None,
        'ogs': False,
        'terry': False,
        'explain': False,
    }
    for name, value in defaults.items():
        if not hasattr(args, name):
            setattr(args, name, value)


def parse_args(argv: list[str] | None = None) -> ap.Namespace:
    argv, rawArgValues = preprocessArgv(argv)
    firstArg = argv[0] if argv else None
    if firstArg in COMMANDS:
        parser = createCommandParser()
        args = parser.parse_args(argv)
    else:
        parser = createDirectParser()
        args = parser.parse_args(argv)
        args.command = None

    fillMissingArgs(args)
    args.compileArgsRaw = rawArgValues['compileArgsRaw']
    args.programArgsRaw = rawArgValues['programArgsRaw']
    args.compileArgs = parseArgumentValues(args.compileArgsRaw)
    args.programArgs = parseArgumentValues(args.programArgsRaw)

    if args.command == 'doctor' and args.doctorTarget:
        if args.doctorTarget == 'languages':
            args.doctorLanguages = True
    elif args.command is None:
        args.targetfile = args.target

    return args
