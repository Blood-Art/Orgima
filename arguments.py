import argparse

parser = argparse.ArgumentParser(description="Origma Args")
parser.add_argument(
    "-d",
    "--directory",
    type=str,
    help="Input for a directory path to organize",
)
parser.add_argument(
    "-c",
    "--count",
    type=int,
    default=3,
    help="Set the image count limit per directory. (default: %(default)s)",
)

parser.add_argument(
    "-ih",
    "--hidden",
    default=False,
    help="Wether to include hidden directories or not. (default: %(default)s)",
    action="store_true",
)


def get_arguments():
    args = parser.parse_args()
    return args
