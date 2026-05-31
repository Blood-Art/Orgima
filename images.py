from Cryptodome.Cipher.AES import new
from pathlib import Path
from config import (
    LOGGER,
    IMAGE_EXTENSIONS,
    MAXIMUM_IMAGE_COUNT_PER_DIRECTORY,
)

from directories import Directory
import re
import sys


class Image:
    directories_count: int = 0
    root_directory_path: Path = Path()
    directory_list: list[Directory] = []

    @classmethod
    def initialize_directory_images(cls, directory_path: Path) -> None:
        """Check for if the directory path is valid and assign it"""
        if not directory_path.exists():
            Directory.log_missing_directory()
            sys.exit(1)

        if not directory_path.is_dir():
            return

        cls.root_directory_path = directory_path
        directory: Directory = Directory(directory_path)
        directory.images_list, directory.image_count = cls.get_sorted_images(
            directory_path
        )
        directory.name = directory_path.name
        directory.root_directory_path = cls.root_directory_path

        if not directory.images_list:
            LOGGER.info(
                f"No images were found in '{directory.name}' -> Checking for Child Directories"
            )
            Directory.process_all_directories(cls.root_directory_path)

        else:
            LOGGER.info(f"{directory.path.name} has '{directory.image_count}' images")

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
    def process_all_directories(cls):
        for directory in cls.directory_list:
            LOGGER.info(f"Processing {directory.name}'s images")
            if directory.images_list is None:
                continue
            cls.process_all_images(directory)

    @classmethod
    def process_all_images(cls, directory: Directory):
        cls.remove_upscaled_duplicates(directory)
        temp_names_list = cls.set_temp_names(directory)
        if temp_names_list is None:
            return

        for idx, image in enumerate(temp_names_list):
            cls.move_images_to_free_directory(directory, image, idx)

        LOGGER.info("Task Finished")

    """ Need to handle edgecase where the image names are not sequential like 1, 3 causes overwriting """

    @classmethod
    def move_images_to_free_directory(
        cls, directory: Directory, image: Path, image_index: int
    ):
        if Directory.is_directory_pass_limit(directory):
            free_directory: Directory | None = Directory.find_free_directory(
                cls.directory_list
            )
            """ Create A New Directory """
            if free_directory is None:
                print("Free directory is None")
                return

            image_destination_path: Path = free_directory.path / (
                str(
                    free_directory.image_count
                    + image_index
                    + 1
                    - directory.images_moved
                )
                + image.suffix
            )
            directory.image_count -= 1
            free_directory.image_count += 1
            directory.images_moved += 1
            print(f"moved {image.name} from {directory.name} to {free_directory.name}")
        else:
            image_destination_path: Path = directory.path / (
                str(image_index + 1 - directory.images_moved) + image.suffix
            )

        image.rename(image_destination_path)

    @classmethod
    def set_temp_names(cls, directory: Directory) -> list[Path] | None:
        if directory.images_list is None:
            return
        images_list: list[Path] = directory.images_list
        temp_names_list = []
        for image in images_list:
            temp_name = image.rename(directory.path / f"temp_{image.name}")
            temp_names_list.append(temp_name)

        return temp_names_list

    @classmethod
    def remove_upscaled_duplicates(cls, directory: Directory) -> None:
        upscaled_images_list = []
        if directory.images_list is None:
            return
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
