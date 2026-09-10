from collections.abc import Callable
from time import perf_counter

from config import LOGGER


def confirmation(message: str) -> bool:
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

