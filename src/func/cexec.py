import os, time, subprocess, sys, constants as c

def exec(full_path, outputfile, args, runOnCompile):
    if os.name == 'nt':
        outputfile += ".exe"
    
    try:
        starttime = time.time()
        
        subprocess.run(
            (f'{c.gcc_path} "{full_path}" -o "{outputfile}" && ./{outputfile}') if runOnCompile else
            (f'{c.gcc_path} "{full_path}" -o "{outputfile}"'),
            check=True,
            shell=True,
            stdout=sys.stdout,
            stderr=sys.stderr,
            text=True
        )
        
        endtime = time.time()
        timetaken = endtime - starttime
        print(f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI]{c.Colours.ENDC} Script executed succesfully.")
        if runOnCompile:
            print(f"{c.Colours.CYAN}Compiled and run in {timetaken:.2f} seconds.{c.Colours.ENDC}\n")
        else:
            print(f"{c.Colours.CYAN}Compiled in {timetaken:.2f} seconds.{c.Colours.ENDC}\n")
        
    except subprocess.CalledProcessError as e:
        print(f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI]{c.Colours.ENDC} {c.Colours.RED}Error:{c.Colours.ENDC} Command failed with return code {e.returncode}.\n")
    except FileNotFoundError: 
        print(f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI]{c.Colours.ENDC} {c.Colours.RED}Error:{c.Colours.ENDC} Gcc not found in PATH.\n")
    except Exception as e:
        print(f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI]{c.Colours.ENDC} {c.Colours.RED}Error:{c.Colours.ENDC} An unexpected error occured {e}.\n")
    