import argparse


class Arguments:
    parser = argparse.ArgumentParser(description="Origma Args")
    parser.add_argument(
        "path",
        type=str,
        help="Input Path for a directory or image path to modify.",
    )
    parser.add_argument(
        "-c",
        "--count",
        type=int,
        default=100,
        help="Set the image count limit per directory. (default: %(default)s)",
    )

    parser.add_argument(
        "-H",
        "--include_hidden",
        default=False,
        help="Whether to include hidden directories or not. (default: %(default)s)",
        action="store_true",
    )
    parser.add_argument(
        "-d",
        "--disable_remove_duplicates",
        default=False,
        help="Whether to disable removing non-upscaled duplicate images (default: %(default)s)",
        action="store_true",
    )

    parser.add_argument(
        "-R",
        "--enable_rounding",
        default=False,
        help="Whether to enable rounding images or not. (default: %(default)s)",
        action="store_true",
    )

    parser.add_argument(
        "-r",
        "--radius",
        default=15,
        type=int,
        help="Set the rounding radius, this is capped at 100. (default: %(default)s)",
    )

    @staticmethod
    def get_arguments():
        args = Arguments.parser.parse_args()
        return args
