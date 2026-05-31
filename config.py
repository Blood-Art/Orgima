from logging import Logger, getLogger, basicConfig, DEBUG
from pathlib import Path

IMAGE_EXTENSIONS: list[str] = [".jpg", ".png", ".jpeg", ".webp"]
LOGGER: Logger = getLogger(__name__)
MAXIMUM_IMAGE_COUNT_PER_DIRECTORY: int = 100
ORIGINAL_DIRECTORY_PATH = Path()
DIRECTORY_NAMES = [
    "alpha",
    "beta",
    "gamma",
    "delta",
    "epsilon",
    "zeta",
    "sigma",
    "omega",
]
basicConfig(
    level=DEBUG,
    format="[%(levelname)s] - [%(asctime)s] - [%(message)s]",
    datefmt="%I:%M:%S %p",
)
