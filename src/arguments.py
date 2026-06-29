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
        action="store_true",
        help="Whether to include hidden directories or not. (default: %(default)s)",
    )
    parser.add_argument(
        "-d",
        "--disable_remove_duplicates",
        default=False,
        action="store_true",
        help="Whether to disable removing non-upscaled duplicate images (default: %(default)s)",
    )

    parser.add_argument(
        "-R",
        "--enable_rounding",
        default=False,
        action="store_true",
        help="Whether to enable rounding images or not. (default: %(default)s)",
    )

    parser.add_argument(
        "-r",
        "--radius",
        default=15,
        type=int,
        help="Set the rounding radius, this is capped at 100. (default: %(default)s)",
    )

    parser.add_argument(
        "-p",
        "--prefix",
        default="",
        type=str,
        help="Set a prefix (name before index) for the image/s",
    )
    parser.add_argument(
        "-s",
        "--suffix",
        default="",
        type=str,
        help="Set a suffix (name after index) for the image/s",
    )

    parser.add_argument(
        "-e",
        "--no_extension",
        default=False,
        action="store_true",
        help="Don't include the images extension (format) (default: %(default)s)",
    )

    parser.add_argument(
        "-U",
        "--enable_upscale",
        default=False,
        action="store_true",
        help="Enable image upscaling using the 'realesrgan-ncnn-vulkan' tool",
    )

    parser.add_argument(
        "-u",
        "--upscale_amount",
        default=2,
        type=int,
        help="Upscale amount by an integer value",
    )

    @staticmethod
    def get_arguments():
        # args = Arguments.parser.parse_args()
        args, tools_args = Arguments.parser.parse_known_args()
        return args, tools_args
