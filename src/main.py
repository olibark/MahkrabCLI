import argparse as ap

def argA():
    print("argA")
    
def argB():
    print("argB")
    
def argC():
    print("argC") 
    
def test(targetfile: str):
    print(f"target-file: {targetfile}")
    
def output_test(outfile: str):
    print(f"output-file: {outfile}")

def main():
    parser = ap.ArgumentParser(
        prog='MAHKRAB-CLI', 
        description="A script to demonstrate command-line flags."
        )
    
    parser.add_argument('-a', '--argA', action="store_true", help="Execute function argA")
    parser.add_argument('-b', '--argB', action="store_true", help="Execute function argB")
    parser.add_argument('-c', '--argC', action="store_true", help="Execute function argC")
    parser.add_argument('-o', '--output', type=str, metavar='file', help="Name of output file")
    parser.add_argument('file', nargs='?', type=str, help="Pass file to function")
    
    args = parser.parse_args()
    
    actions = {
        'argA': lambda: argA(), 
        'argB': lambda: argB(), 
        'argC': lambda: argC(),
        'file': lambda: test(args.file), 
        'output': lambda: output_test(args.output)
    }
    
    for name, func in actions.items():
        if getattr(args, name):
            func()
            
main()