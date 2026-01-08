import subprocess, sys
import argparse as ap

from mahkrab.tools.decorators.timers import compileruntime, compiletime
from mahkrab import constants as c

class Executor:
    @staticmethod
    def exec(full_path: str, outputfile: str, args: ap.Namespace, runOnCompile: bool) -> None:
        if c.osName == "windows":
            print(
                f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI] -{c.Colours.ENDC} {c.Colours.RED}"
                f"Error:{c.Colours.ENDC} Not supported on windows{c.Colours.RED}{c.Colours.ENDC}.\n"
            )
            return
            
        objfile = f"{outputfile}.o"
        cmd = [c.NASM_PATH, "-f", "elf64", full_path, "-o", objfile]
        
        try:
            if runOnCompile:
                run_cmd = [f"./{outputfile}"]
                Executor.runOnCompile(cmd, objfile, outputfile, run_cmd)
            else:
                Executor.compile(cmd, objfile, outputfile)
            
        except subprocess.CalledProcessError as e:
            print(
                f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI] -{c.Colours.ENDC} {c.Colours.RED}"
                f"Error:{c.Colours.ENDC} Command failed with return code {c.Colours.RED}{e.returncode}{c.Colours.ENDC}.\n"
            )
        except FileNotFoundError: 
            print(
                f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI] -{c.Colours.ENDC} {c.Colours.RED}"
                f"Error:{c.Colours.ENDC} Nasm not found in {c.Colours.RED}PATH{c.Colours.ENDC}.\n"
            )
        except Exception as e:
            print(
                f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI] -{c.Colours.ENDC} {c.Colours.RED}"
                f"Error:{c.Colours.ENDC} An unexpected error occured {c.Colours.RED}{e}{c.Colours.RED}.\n"
            )

    @staticmethod
    @compiletime
    def compile(cmd: list[str], objfile: str, outputfile: str) -> None:
        subprocess.run(
            cmd,
            check=True,
            stdout=sys.stdout,
            stderr=sys.stderr,
            text=True,
        )
        Executor.link(objfile, outputfile)
    
    def link(objfile: str, outputfile: str) -> None:
        link_cmd = ["ld", "-o", outputfile, objfile]
        
        subprocess.run(
            link_cmd,
            check=True, 
            stdout=sys.stdout,
            stderr=sys.stderr,
            text=True,
        )
    
    @staticmethod
    @compileruntime
    def runOnCompile(cmd: list[str], objfile: str, outputfile: str, run_cmd: list[str]) -> None:
        subprocess.run(
            cmd,
            check=True,
            stdout=sys.stdout,
            stderr=sys.stderr,
            text=True,
        )
        Executor.link(objfile, outputfile)
        
        subprocess.run(
            run_cmd,
            check=True,
            stdout=sys.stdout,
            stderr=sys.stderr,
            text=True,
        )
