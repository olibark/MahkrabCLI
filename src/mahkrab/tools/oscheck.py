import os

def findOS() -> str:
    if os.name == 'nt':
        return "windows"
    else: 
        return "unixlike"