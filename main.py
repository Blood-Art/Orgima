#!/usr/bin/env python
from images import Image
import config
from pathlib import Path


def main():
    directory_path = Path(input("Enter Directory Path : "))
    config.ORIGINAL_DIRECTORY_PATH = directory_path
    Image.initialize_directory_images(directory_path)
    Image.process_all_images()


if __name__ == "__main__":
    main()
