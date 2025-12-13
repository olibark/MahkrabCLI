import os

GCC_PATH = 'gcc'
PYTHON_PATH = 'python3'

SOURCE_DIR = os.path.dirname(os.path.abspath(__file__)) #MahkrabCLI/src
BASE_DIR = os.path.dirname(SOURCE_DIR)
ASSETS_DIR = os.path.join(SOURCE_DIR, "assets")
TERRY_FILE = os.path.join(ASSETS_DIR, "terry.txt")

class Colours: 
    """ansi colour codes"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    ENDC = '\033[0m'
    
CLEAR = 'cls' if os.name == 'nt' else 'clear'