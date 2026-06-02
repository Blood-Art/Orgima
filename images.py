from Cython.Compiler.Naming import self_cname
from importlib.resources import path
import config
from pathlib import Path
from config import (
    LOGGER,
    IMAGE_EXTENSIONS,
    MAXIMUM_IMAGE_COUNT_PER_DIRECTORY,
    DIRECTORY_NAMES,
)

from directories import Directory
import re
import sys


class Image:
    directories_count: int = 0
    root_directory_path: Path = Path()
    directory_list: list[Directory] = []

    @classmethod
    def initalize_directory_objects(cls, directory_path: Path) -> None:
        """Check for if the directory path is valid and assign it"""
        if not directory_path.exists():
            Directory.log_missing_directory("Invalid input no such path exists")
            sys.exit(1)

        if not directory_path.is_dir():
            Directory.log_missing_directory("This is not a directory")
            sys.exit(1)

        directory: Directory = Directory(directory_path)
        directory.images_list, directory.image_count = cls.get_sorted_images(
            directory_path
        )
        directory.name = directory_path.name
        directory.root_directory_path = cls.root_directory_path

        if directory.is_empty():
            return
        if directory.is_empty_of_images():
            LOGGER.info(
                f"No images were found in [{directory.name}] -> Checking for Child Directories"
            )
            Directory.process_all_directories(cls.root_directory_path)

        """ Exclude Root Directory """
        if directory.path is not cls.root_directory_path:
            cls.directory_list.append(directory)

    @classmethod
    def get_sorted_images(cls, directory_path: Path) -> tuple[list[Path], int]:
        images_list: list[Path] = []

        """ Accept only images """
        for image in directory_path.iterdir():
            if image.suffix not in IMAGE_EXTENSIONS:
                continue
            images_list.append(image)

        number_of_images: int = len(images_list)

        return sorted(
            images_list, key=lambda img: Path(img).stat().st_ctime
        ), number_of_images

    @classmethod
    def process_directory_images(cls):
        for directory in cls.directory_list:
            LOGGER.info(f"Processing {directory.name}'s images")
            cls.process_all_images(directory)

    @classmethod
    def process_all_images(cls, directory: Directory):
        cls.check_directory_size(directory)
        # cls.remove_upscaled_duplicates(directory)
        # temp_names_list = cls.set_temp_names(directory)
        # if temp_names_list is None:
        #     return

        # for idx, image in enumerate(temp_names_list):
        #     pass

        LOGGER.info("Task Finished")

    """ Need to handle edgecase where the image names 
    are not sequential like 1, 3 causes overwriting 
    the fix to this is probably not renaming the moved image and keeping it's temp name"""

    @classmethod
    def check_directory_size(cls, directory: Directory):
        if directory.is_empty():
            return

        if directory.is_pass_size_limit():
            LOGGER.warning(
                f"{directory.name} has passed the size limit of '{MAXIMUM_IMAGE_COUNT_PER_DIRECTORY}'"
            )
            LOGGER.info("Freeing up some space...")

        for index, image in enumerate(directory.images_list):
            if directory.is_pass_size_limit():
                cls.move_images_to_free_directory(directory, image, index)
            else:
                break

    @classmethod
    def move_images_to_free_directory(
        cls, current_directory: Directory, image: Path, image_index: int
    ):
        free_directory = Directory.find_free_directory(cls.directory_list)
        # new_directory = None
        # if free_directory is None:
        #
        # if new_directory is not None:

        # if Directory.all_directories_full():
        #     free_directory = new_directory

        # free_directories: list[Directory] = []
        # free_directories.append(free_directory)
        # if Directory.all_directories_full() and current_directory.is_pass_size_limit():
        #     new_directory: Directory = Directory.create_new_directory()
        # free_directory = new_directory
        # free_directories.append(new_directory)
        # LOGGER.warning("All directories are full...")
        # LOGGER.info(f"Created new directory '{new_directory.name}'")
        # cls.directory_list.append(new_directory)

        image_destination = (
            free_directory.path
            / f"moved_{free_directory.image_count + 1}{image.suffix}"
        )

        image.move(image_destination)

        current_directory.image_count -= 1
        free_directory.images_moved += 1
        free_directory.image_count += 1
        if current_directory.is_full():
            for dir in Directory.free_directories_list:
                dir.log_images_moved()

    @classmethod
    def rename_images(cls, directory: Directory):
        temp_names_list: list[Path] | None = cls.set_temp_names(directory)
        if temp_names_list is None:
            return
        for image_index, image in enumerate(temp_names_list):
            ...

    @classmethod
    def set_temp_names(cls, directory: Directory) -> list[Path] | None:
        images_list: list[Path] = directory.images_list
        temp_names_list = []
        for image in images_list:
            temp_name = image.rename(directory.path / f"temp_{image.name}")
            temp_names_list.append(temp_name)

        return temp_names_list

    @classmethod
    def remove_upscaled_duplicates(cls, directory: Directory) -> None:
        upscaled_images_list = []
        images_list: list[Path] = directory.images_list
        for image in images_list:
            if ("upscayl") not in image.name:
                continue
            LOGGER.info(f"Found upscaled image '{image.name}'")
            match = re.match(r"^[^_]+", image.name)
            if match:
                upscaled_images_list.append(match.group())

        """ Delete the non-upscaled version of images """
        for image in images_list:
            if image.stem in upscaled_images_list:
                LOGGER.info(f"Deleted duplicate {image.name} image")
                image.unlink(missing_ok=True)
                images_list.remove(image)
