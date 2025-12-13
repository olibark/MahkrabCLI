import os, time, subprocess, sys, constants as c
class Executor:
    def exec(full_path, outputfile, args, runOnCompile) -> None:
        if os.name == 'nt':
            outputfile += ".exe"
        
        try:
            starttime = time.time()
            
            subprocess.run(
                (f'{c.GCC_PATH} "{full_path}" -o "{outputfile}" && ./{outputfile}') if runOnCompile else
                (f'{c.GCC_PATH} "{full_path}" -o "{outputfile}"'),
                check=True,
                shell=True,
                stdout=sys.stdout,
                stderr=sys.stderr,
                text=True
            )
            
            endtime = time.time()
            timetaken = endtime - starttime
            print(f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI] -{c.Colours.ENDC} Script executed succesfully")
            if runOnCompile:
                print(f"{c.Colours.CYAN}Compiled and ran in {c.Colours.BLUE}{timetaken:.2f}{c.Colours.CYAN} seconds.{c.Colours.ENDC}\n")
            else:
                print(f"{c.Colours.CYAN}Compiled in {c.Colours.BLUE}{timetaken:.2f}{c.Colours.CYAN} seconds.{c.Colours.ENDC}\n")
            
        except subprocess.CalledProcessError as e:
            print(f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI] -{c.Colours.ENDC} {c.Colours.RED}Error:{c.Colours.ENDC} Command failed with return code {c.Colours.RED}{e.returncode}{c.Colours.ENDC}.\n")
        except FileNotFoundError: 
            print(f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI] -{c.Colours.ENDC} {c.Colours.RED}Error:{c.Colours.ENDC} Gcc not found in {c.Colours.RED}PATH{c.Colours.ENDC}.\n")
        except Exception as e:
            print(f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI] -{c.Colours.ENDC} {c.Colours.RED}Error:{c.Colours.ENDC} An unexpected error occured {c.Colours.RED}{e}{c.Colours.RED}.\n")
    
    def runbin(targetfile, args) -> None:
        try:
            startime = time.time()
            if not os.path.exists(f"build/{targetfile}"):
                subprocess.run(
                    f'./{targetfile}',
                    check=True,
                    shell=True,
                    stdout=sys.stdout,
                    stderr=sys.stderr,
                    text=True
                )
            elif os.path.exists(f"build/{targetfile}"):
                
                subprocess.run(
                    f'./build/{targetfile}',
                    check=True,
                    shell=True,
                    stdout=sys.stdout,
                    stderr=sys.stderr,
                    text=True
                )
            
            endtime = time.time()
            timetaken = endtime - startime
            
            print(f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI] -{c.Colours.ENDC} Script executed succesfully")
            print(f"{c.Colours.CYAN}Run in {c.Colours.BLUE}{timetaken:.2f}{c.Colours.CYAN} seconds.{c.Colours.ENDC}\n")
            
        except subprocess.CalledProcessError as e:
            print(f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI] -{c.Colours.ENDC} {c.Colours.RED}Error:{c.Colours.ENDC} Command failed with return code {c.Colours.RED}{e.returncode}{c.Colours.ENDC}.\n")
        except FileNotFoundError: 
            print(f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI] -{c.Colours.ENDC} {c.Colours.RED}Error:{c.Colours.ENDC} Gcc not found in {c.Colours.RED}PATH{c.Colours.ENDC}.\n")
        except Exception as e:
            print(f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI] -{c.Colours.ENDC} {c.Colours.RED}Error:{c.Colours.ENDC} An unexpected error occured {c.Colours.RED}{e}{c.Colours.RED}.\n")