import argparse as ap
import shlex

from mahkrab.tools.getversion import get_version

COMMANDS = {'run'}

def parseProgramArgs(rawArgs: list[list[str]], unknownArgs: list[str]) -> list[str]:
    args: list[str] = []

    for rawArgGroup in rawArgs:
        for rawArg in rawArgGroup:
            args.extend(shlex.split(rawArg))

    if unknownArgs and unknownArgs[0] == '--':
        unknownArgs = unknownArgs[1:]

    if unknownArgs:
        args.extend(unknownArgs)

    return args

def parse_args(argv: list[str] | None = None) -> ap.Namespace:
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
        '--program-args', '--tool-args',
        dest='programArgsRaw',
        action='append',
        nargs='*',
        default=[],
        metavar='<args>',
        help='Extra compiler/interpreter args (supports quoted values).',
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
    
    args, unknown = parser.parse_known_args(argv)

    if unknown and not args.programArgsRaw:
        parser.error(f'unrecognized arguments: {" ".join(unknown)}')
    
    args.command = None
    args.targetfile = None
    args.programArgs = parseProgramArgs(args.programArgsRaw, unknown)
    
    if args.target in COMMANDS: 
        args.command = args.target
    else:
        args.targetfile = args.target
    
    return args
