from collections.abc import Callable
from time import perf_counter

from config import ARGUMENTS, LOGGER


def confirmation(message: str) -> bool:
    if ARGUMENTS.no_prompt:
        return True
    while True:
        confirmation: str = input(f"{message} (y/n) ").lower()
        if confirmation == "y" or confirmation == "":
            return True
        elif confirmation == "n":
            return False

def time_function(fn: Callable, *args, **kwargs):
    start_time: float = perf_counter()
    result = fn(*args, **kwargs)
    finish_time: float = perf_counter()
    LOGGER.info(f"Task Finished in {finish_time - start_time:0.2f} Seconds")
    return result

def convert_str_resolution_to_tuple(resolution: str) -> tuple[int, int]:
    width, height = map(int, resolution.lower().split("x"))
    return (width, height)
    

