import time
from functools import wraps

from mahkrab import constants as c

def runtime(func) -> callable:
    @wraps(func)
    def timer(*args, **kwargs) -> any:
        starttime = time.perf_counter()
        result = func(*args, **kwargs)
        endtime = time.perf_counter()
        timetaken = endtime - starttime
        
        print(
            f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI] -{c.Colours.ENDC} Script executed succesfully"
        )
        print(
            f"{c.Colours.CYAN}Executed in {c.Colours.BLUE}{timetaken}{c.Colours.CYAN} seconds.{c.Colours.ENDC}\n"
        )
        
        return result
    return timer

def compiletime(func) -> callable:
    @wraps(func)
    def timer(*args, **kwargs) -> any:
        starttime = time.perf_counter()
        result = func(*args, **kwargs)
        endtime = time.perf_counter()
        timetaken = endtime - starttime
        
        print(
            f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI] -{c.Colours.ENDC} Script executed succesfully"
        )
        print(
            f"{c.Colours.CYAN}Compiled in {c.Colours.BLUE}{timetaken}{c.Colours.CYAN} seconds.{c.Colours.ENDC}\n"
        )
        
        return result
    return timer

def compileruntime(func):
    @wraps(func)
    def timer(*args, **kwargs) -> any:
        starttime = time.perf_counter()
        result = func(*args, **kwargs)
        endtime = time.perf_counter()
        timetaken = endtime - starttime
        
        print(
            f"\n{c.Colours.MAGENTA}[MAHKRAB-CLI] -{c.Colours.ENDC} Script executed succesfully"
        )
        print(
            f"{c.Colours.CYAN}Compiled and run in {c.Colours.BLUE}{timetaken}{c.Colours.CYAN} seconds.{c.Colours.ENDC}\n"
        )
        return result
    return timer
        
