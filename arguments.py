import argparse


class Arguments:
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
        default=100,
        help="Set the image count limit per directory. (default: %(default)s)",
    )

    parser.add_argument(
        "-i",
        "--include_hidden",
        default=False,
        help="Wether to include hidden directories or not. (default: %(default)s)",
        action="store_true",
    )
    parser.add_argument(
        "-drd",
        "--disable_remove_duplicates",
        default=False,
        help="Wether to disable removing non-upscaled duplicate images (default: %(default)s)",
        action="store_true",
    )

    def get_arguments():
        args = Arguments.parser.parse_args()
        return args
