from lutris.util.amazon.sds_proto2 import Dir
from pathlib import Path
from config import (
    LOGGER,
    IMAGE_EXTENSIONS,
    MAXIMUM_IMAGE_COUNT_PER_DIRECTORY,
)

from directories import Directory
import re


class Image:
    directories_count: int = 0
    directory_path: Path = Path()
    directory_list: list[Directory] = []

    @classmethod
    def initialize_directory_images(cls, directory_path: Path) -> None:
        """Check for if the directory path is valid and assign it"""
        if not Directory.directory_exists(directory_path):
            return

        cls.directory_path = directory_path
        directory: Directory = Directory(directory_path)
        directory.images_list, directory.image_count = cls.get_sorted_images(
            directory_path
        )[0]
        directory.name = directory_path.name

        if not directory.images_list:
            LOGGER.info(
                f"No images were found in '{directory.name}' -> Checking for child directories"
            )
            Directory.process_all_directories(cls.directory_path)
            return

        else:
            LOGGER.info(
                f"Found '{directory.image_count}' images in {cls.directory_path.name}"
            )

        cls.directory_list.append(directory)

    @classmethod
    def get_sorted_images(cls, directory_path: Path) -> tuple[list[Path], int]:
        images_list: list[Path] = []

        """ Accept only images """
        for image in Path.iterdir(directory_path):
            if image.suffix not in IMAGE_EXTENSIONS:
                continue
            images_list.append(image)

        number_of_images: int = len(images_list)

        return sorted(
            images_list, key=lambda img: Path(img).stat().st_ctime
        ), number_of_images

    @classmethod
    def process_all_images(cls):
        directories_image_counts: list[int[0]] = [
            directory.image_count for directory in cls.directory_list
        ]
        print(directories_image_counts)
        for index, directory in enumerate(cls.directory_list):
            LOGGER.info(f"Processing {directory.name}'s images")
            if directory.images_list is None:
                continue
            # if directory.image_count < MAXIMUM_IMAGE_COUNT_PER_DIRECTORY:
            #     cls.remove_upscaled_duplicates(directory)
            #     temp_names_list = cls.set_temp_names(directory)
            #     if temp_names_list is None:
            #         continue
            #     for idx, image in enumerate(temp_names_list):
            #         image.rename(image.with_stem(str(idx + 1)))
            #
            #     LOGGER.info("Task Finished")
            # else:
            #     print(f"Directory {directory.name} is full", directory.image_count)

    @classmethod
    def set_temp_names(cls, directory: Directory) -> list[Path] | None:
        if directory.images_list is None:
            return
        images_list: list[Path] = directory.images_list
        temp_names_list = []
        for image in images_list:
            temp_name = image.rename(directory.directory_path[0] / f"temp_{image.name}")
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
