import os, subprocess, sys, time

from mahkrab import constants as c 

class Executor:
    @staticmethod
    def exec(full_path, outputfile, args, runOnCompile) -> None:
        if os.name == 'nt' and not outputfile.endswith('.exe'):
            outputfile += ".exe"
        
        try:
            starttime = time.time()
            
            subprocess.run(
                [c.GCC_PATH, full_path, '-o', outputfile],
                check=True,
                stdout=sys.stdout,
                stderr=sys.stderr,
                text=True,
            )
            
            if runOnCompile:
                run_cmd = (
                    [outputfile] if os.name == 'nt' else [f'./{outputfile}']
                )
                subprocess.run(
                    run_cmd, 
                    check=True,
                    stdout=sys.stdout,
                    stderr=sys.stderr,
                    text=True,
                )
            
            endtime = time.time()
            timetaken = endtime - starttime
            
            print(
                f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI] -{c.Colours.ENDC} Script executed succesfully"
            )
            if runOnCompile:
                print(
                    f"{c.Colours.CYAN}Compiled and ran in {c.Colours.BLUE}{timetaken:.2f}{c.Colours.CYAN} seconds.{c.Colours.ENDC}\n"
                )
            else:
                print(
                    f"{c.Colours.CYAN}Compiled in {c.Colours.BLUE}{timetaken:.2f}{c.Colours.CYAN} seconds.{c.Colours.ENDC}\n"
                )
            
        except subprocess.CalledProcessError as e:
            print(
                f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI] -{c.Colours.ENDC} {c.Colours.RED}"
                f"Error:{c.Colours.ENDC} Command failed with return code {c.Colours.RED}{e.returncode}{c.Colours.ENDC}.\n"
            )
        except FileNotFoundError: 
            print(
                f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI] -{c.Colours.ENDC} {c.Colours.RED}"
                f"Error:{c.Colours.ENDC} Gcc not found in {c.Colours.RED}PATH{c.Colours.ENDC}.\n"
            )
        except Exception as e:
            print(
                f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI] -{c.Colours.ENDC} {c.Colours.RED}"
                f"Error:{c.Colours.ENDC} An unexpected error occured {c.Colours.RED}{e}{c.Colours.RED}.\n"
            )
    
    @staticmethod
    def runbin(targetfile, args) -> None:
        try:
            starttime = time.time()
            
            build_path = os.path.join("build", targetfile)
            run_path = build_path if os.path.exists(build_path) else targetfile
            
            run_cmd = (
                [run_path] if os.name == 'nt' else [f"./{run_path}"]
            )
            
            subprocess.run(
                run_cmd, 
                check=True,
                stdout=sys.stdout,
                stderr=sys.stderr,
                text=True,
            )
            
            endtime = time.time()
            timetaken = endtime - starttime
            
            print(
                f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI] -{c.Colours.ENDC} Script executed succesfully"
            )
            print(
                f"{c.Colours.CYAN}Run in {c.Colours.BLUE}{timetaken:.2f}{c.Colours.CYAN} seconds.{c.Colours.ENDC}\n"
            )
            
        except subprocess.CalledProcessError as e:
            print(
                f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI] -{c.Colours.ENDC} {c.Colours.RED}"
                f"Error:{c.Colours.ENDC} Command failed with return code {c.Colours.RED}{e.returncode}{c.Colours.ENDC}.\n"
            )
        except FileNotFoundError: 
            print(
                f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI] -{c.Colours.ENDC} {c.Colours.RED}"
                f"Error:{c.Colours.ENDC} Binary not found in {c.Colours.RED} directory{c.Colours.ENDC}.\n"
            )
        except Exception as e:
            print(
                f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI] -{c.Colours.ENDC} {c.Colours.RED}"
                f"Error:{c.Colours.ENDC} An unexpected error occured {c.Colours.RED}{e}{c.Colours.RED}.\n"
            )