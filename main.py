#!/usr/bin/env python
from directories import Directory
from images import Image
from pathlib import Path


def main():
    directory_path = Path(input("Enter Directory Path : "))
    Image.initialize_directory_images(directory_path)
    Image.process_all_directories()


if __name__ == "__main__":
    main()
