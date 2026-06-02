import argparse

parser = argparse.ArgumentParser(description="Origma Args")
parser.add_argument(
    "-d",
    "--directory",
    type=str,
    help="Input for a directory path to organize",
)


def get_arguments():
    args = parser.parse_args()
    return args
