#!/usr/bin/env python
from directories import Directory
from images import Image
from pathlib import Path
import sys
import arguments


"""Check for if the directory path is valid and assign it"""


def validate_directory_input(directory: Path):
    if not directory.exists():
        Directory.log_directory_error("Invalid input no such path exists ❌")
        sys.exit(1)
    if not directory.is_dir():
        Directory.log_directory_error("This is not a directory ❌")
        sys.exit(1)


def main():
    args = arguments.get_arguments()
    directory_path = Path(args.directory)
    validate_directory_input(directory_path)
    Directory.ROOT_DIRECTORY_PATH = directory_path
    Image.initalize_directory_objects(directory_path)
    Image.process_directory_images()


if __name__ == "__main__":
    main()
