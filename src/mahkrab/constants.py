from __future__ import annotations
import os, sys
from pathlib import Path

from mahkrab.tools.oscheck import findOS

osName = findOS()

GCC_PATH = os.environ.get("MAHKRAB_GCC", "gcc")
NASM_PATH = os.environ.get("MAHKRAB_NASM", "nasm")
PYTHON_PATH = os.environ.get("MAHKRAB_PYTHON", sys.executable)
GPP_PATH = os.environ.get("MAHKRAB_GPP", "g++")
RUSTC_PATH = os.environ.get("MAHKRAB_RUSTC", "rustc")
GO_PATH = os.environ.get("MAHKRAB_GO", "go")
JAVAC_PATH = os.environ.get("MAHKRAB_JAVAC", "javac")
JAVA_PATH = os.environ.get("MAHKRAB_JAVA", "java")
NODE_PATH = os.environ.get("MAHKRAB_NODE", "node")
TS_NODE_PATH = os.environ.get("MAHKRAB_TS", "ts-node")
RUBY_PATH = os.environ.get("MAHKRAB_RUBY", "ruby")
PHP_PATH = os.environ.get("MAHKRAB_PHP", "php")
LUA_PATH = os.environ.get("MAHKRAB_LUA", "lua")
BASH_PATH = os.environ.get("MAHKRAB_BASH", "bash")
PWSH_PATH = os.environ.get("MAHKRAB_PWSH", "pwsh")
PERL_PATH = os.environ.get("MAHKRAB_PERL", "perl")
CSC_PATH = os.environ.get("MAHKRAB_CSC", "csc")
VBC_PATH = os.environ.get("MAHKRAB_VBC", "vbc")
MONO_PATH = os.environ.get("MAHKRAB_MONO", "mono")
SQLITE3_PATH = os.environ.get("MAHKRAB_SQLITE3", "sqlite3")
RSCRIPT_PATH = os.environ.get("MAHKRAB_RSCRIPT", "Rscript")
FPC_PATH = os.environ.get("MAHKRAB_FPC", "fpc")
TURBOWARP_PATH = os.environ.get("MAHKRAB_TURBOWARP", "twcli")
GFORTRAN_PATH = os.environ.get("MAHKRAB_GFORTRAN", "gfortran")
MATLAB_PATH = os.environ.get("MAHKRAB_MATLAB", "matlab")
GNATMAKE_PATH = os.environ.get("MAHKRAB_GNATMAKE", "gnatmake")
SWIFTC_PATH = os.environ.get("MAHKRAB_SWIFTC", "swiftc")
SWIPL_PATH = os.environ.get("MAHKRAB_SWIPL", "swipl")
KOTLINC_PATH = os.environ.get("MAHKRAB_KOTLINC", "kotlinc")
FBC_PATH = os.environ.get("MAHKRAB_FBC", "fbc")
COBC_PATH = os.environ.get("MAHKRAB_COBC", "cobc")
DART_PATH = os.environ.get("MAHKRAB_DART", "dart")

SOURCE_DIR = Path(__file__).resolve().parent
BASE_DIR = SOURCE_DIR.parent
ASSETS_DIR = SOURCE_DIR / "assets"
TERRY_FILE = ASSETS_DIR / "terry.txt"

class Colours:
    """ANSI colour codes."""
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    ENDC = "\033[0m"

CLEAR = "cls" if osName == "windows" else "clear"
