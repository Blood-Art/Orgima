import arguments
from logging import Logger, getLogger, basicConfig, DEBUG

ARGUMENTS = arguments.get_arguments()
IMAGE_EXTENSIONS: list[str] = [".jpg", ".png", ".jpeg", ".webp"]
LOGGER: Logger = getLogger(__name__)
MAXIMUM_IMAGE_COUNT_PER_DIRECTORY: int = ARGUMENTS.count
DIRECTORY_NAMES = (
    "alpha",
    "beta",
    "gamma",
    "delta",
    "epsilon",
    "zeta",
    "sigma",
    "omega",
)
basicConfig(
    level=DEBUG,
    format="[%(levelname)s] - [%(asctime)s] - [%(message)s]",
    datefmt="%I:%M:%S %p",
)
