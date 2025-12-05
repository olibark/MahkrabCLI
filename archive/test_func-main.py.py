import os, constants as c

def test(targetfile: str):
    print(f"target-file: {targetfile}")
    c.targetfile = targetfile
    print(f"Path to file: {os.path.join(os.path.abspath(targetfile))}")
    
    try:
        os.system(f'python3 -u {targetfile}')
    except Exception as e:
        print(f"Error: {e}.")