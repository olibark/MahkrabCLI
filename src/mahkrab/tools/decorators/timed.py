import time
from functools import wraps

from mahkrab import constants as c

@staticmethod
def timed_decorator(func) -> callable:
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
            f"{c.Colours.CYAN}Executed in {c.Colours.BLUE}{timetaken:.2f}{c.Colours.CYAN} seconds.{c.Colours.ENDC}\n"
        )
        
        return result
    return timer