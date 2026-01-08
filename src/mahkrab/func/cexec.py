import subprocess, sys
import argparse as ap

from mahkrab.tools import findDependencies
from mahkrab import constants as c
from mahkrab.tools.decorators.timers import compiletime, compileruntime

class Executor:
    @staticmethod
    def findFlags(full_path: str) -> list[str]:
        flags = findDependencies.findDependencies(full_path)
        
        return flags
    
    @staticmethod
    def exec(full_path: str, outputfile: str, args: ap.Namespace, runOnCompile: bool) -> None:
        if c.osName == "windows" and not outputfile.endswith('.exe'):
            outputfile += ".exe"
        
        flags = Executor.findFlags(full_path)
        
        cmd = [c.GCC_PATH, full_path]
        
        if flags:
            cmd.extend(flags)
        
        cmd.extend(['-o', outputfile])
        
        try:
            if runOnCompile:
                run_cmd = (
                    [outputfile] if c.osName == "windows" else [f'./{outputfile}']
                )
                Executor.runOnCompile(cmd, run_cmd)
            else:
                Executor.compile(cmd)
                
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
    @compiletime
    def compile(cmd: list[str]) -> None:
        subprocess.run(
                cmd,
                check=True, 
                stdout=sys.stdout,
                stderr=sys.stderr,
                text=True,
            )
    
    @staticmethod
    @compileruntime
    def runOnCompile(cmd: list[str], run_cmd: list[str]) -> None:
        subprocess.run(
            cmd,
            check=True,
            stdout=sys.stdout,
            stderr=sys.stderr,
            text=True,
        )
        
        subprocess.run(
            run_cmd,
            check=True,
            stdout=sys.stdout,
            stderr=sys.stderr,
            text=True,
        )
