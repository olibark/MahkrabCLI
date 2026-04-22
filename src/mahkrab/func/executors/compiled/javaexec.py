import subprocess, os, sys
import argparse as ap

from mahkrab import constants as c
from mahkrab.func.executors import status
from mahkrab.tools.decorators.timers import compiletime, compileruntime
from mahkrab.tools.tooloverride import apply_tool_override

class Executor:
    @staticmethod
    def exec(full_path: str, outputfile: str, args: ap.Namespace, runOnCompile: bool) -> int:
        compileArgs = list(getattr(args, 'compileArgs', []))
        programArgs = list(getattr(args, 'programArgs', []))
        classname = os.path.splitext(os.path.basename(full_path))[0]
        out_dir = os.path.dirname(outputfile) or "build"
        
        cmd = apply_tool_override([c.JAVAC_PATH, *compileArgs, "-d", out_dir, full_path], args)
        run_cmd = [c.JAVA_PATH, "-cp", out_dir, classname, *programArgs]
        
        try:
            if runOnCompile:
                Executor.runOnCompile(cmd, run_cmd)
            else:
                Executor.compile(cmd)
            return 0
                
        except subprocess.CalledProcessError as e:
            return status.commandFailure(e)
        except FileNotFoundError: 
            return status.missingTool(f"Java not found in {c.Colours.RED}PATH{c.Colours.ENDC}.")
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
