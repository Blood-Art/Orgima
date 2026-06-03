import argparse

parser = argparse.ArgumentParser(description="Origma Args")
parser.add_argument(
    "-d",
    "--directory",
    type=str,
    help="Input for a directory path to organize",
)
parser.add_argument(
    "-s",
    "--size",
    type=int,
    default=3,
    help="Set the image size limit of a directory default $(default)s",
)


def get_arguments():
    args = parser.parse_args()
    return args
