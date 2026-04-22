import os, subprocess, sys
import argparse as ap

from mahkrab import constants as c
from mahkrab.func.executors import status
from mahkrab.tools.decorators.timers import compiletime, compileruntime
from mahkrab.tools.tooloverride import apply_tool_override

class Executor:
    @staticmethod
    def exec(full_path: str, outputfile: str, args: ap.Namespace, runOnCompile: bool) -> int:
        if c.osName == "windows" and not outputfile.endswith('.exe'):
            outputfile += ".exe"
        
        compileArgs = list(getattr(args, 'compileArgs', []))
        programArgs = list(getattr(args, 'programArgs', []))
        cmd = apply_tool_override([c.RUSTC_PATH, full_path, *compileArgs, "-o", outputfile], args)
        
        try:
            if runOnCompile:
                if c.osName == "windows":
                    run_cmd = [outputfile]
                elif os.path.isabs(outputfile):
                    run_cmd = [outputfile]
                else:
                    run_cmd = [f'./{outputfile}']
                if programArgs:
                    run_cmd.extend(programArgs)
                Executor.runOnCompile(cmd, run_cmd)
            else:
                Executor.compile(cmd)
            return 0
                
        except subprocess.CalledProcessError as e:
            return status.commandFailure(e)
        except FileNotFoundError: 
            return status.missingTool(f"Rustc not found in {c.Colours.RED}PATH{c.Colours.ENDC}.")
        except Exception as e:
            return status.unexpectedFailure(e)
    
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
