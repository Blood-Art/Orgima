#!/usr/bin/env python
from directories import Directory
from images import Image
import arguments
from pathlib import Path


def initialize_root_paths(directory_path: Path):
    Image.root_directory_path = directory_path
    Directory.root_directory_path = directory_path


def main():
    args = arguments.get_arguments()
    directory_path = Path(args.directory)
    initialize_root_paths(directory_path)
    Image.initalize_directory_objects(directory_path)
    Image.process_directory_images()


if __name__ == "__main__":
    main()
