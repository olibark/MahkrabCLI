import argparse as ap
import shlex
import sys

from mahkrab.tools.getversion import get_version

COMMANDS = {'run'}
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

def parse_args(argv: list[str] | None = None) -> ap.Namespace:
    argv, rawArgValues = preprocessArgv(argv)
    parser = ap.ArgumentParser(
        prog="MAHKRAB-CLI",
    )
    parser.add_argument(
        'target',
        nargs="?",
        help='Target file name',
    )
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

    args = parser.parse_args(argv)

    args.command = None
    args.targetfile = None
    args.compileArgsRaw = rawArgValues['compileArgsRaw']
    args.programArgsRaw = rawArgValues['programArgsRaw']
    args.compileArgs = parseArgumentValues(args.compileArgsRaw)
    args.programArgs = parseArgumentValues(args.programArgsRaw)
    
    if args.target in COMMANDS: 
        args.command = args.target
    else:
        args.targetfile = args.target
    
    return args
