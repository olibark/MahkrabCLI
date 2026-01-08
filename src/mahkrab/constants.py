from __future__ import annotations
import os, sys
from pathlib import Path

from mahkrab.tools.oscheck import findOS

osName = findOS()

GCC_PATH = os.environ.get("MAHKRAB_GCC", "gcc")
NASM_PATH = os.environ.get("MAHKRAB_NASM", "nasm")
PYTHON_PATH = os.environ.get("MAHKRAB_PYTHON", sys.executable)

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