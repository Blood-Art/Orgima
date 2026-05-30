#!/usr/bin/env python
from images import Image
import config
from pathlib import Path


def main():
    directory_path = Path(input("Enter Directory Path : "))
    config.ORIGINAL_DIRECTORY_PATH = directory_path
    Image.arrange_images(directory_path)


if __name__ == "__main__":
    main()
