"""Import config file for MAXIMUM_IMAGE_COUNT_PER_DIRECTORY to update across files"""

import config
from config import (
    MAXIMUM_IMAGE_COUNT_PER_DIRECTORY,
    LOGGER,
    DIRECTORY_NAMES,
)
from typing import List
from pathlib import Path


class Directory:
    sorted_directories_stack: List[Path] = []
    directories_count: int = 0

    def __init__(
        self,
        directory_path: Path,
        image_count: int = 0,
        images_list: List[Path] | None = None,
        name: str = "",
    ):
        self.directory_path = (directory_path,)
        self.image_count = (image_count,)
        self.images_list = images_list
        self.name = name

    @classmethod
    def directory_exists(cls, directory_path: Path) -> bool:
        if not Path.exists(directory_path):
            LOGGER.error("Invalid input no such path exists")
            LOGGER.info("Exiting...")
            return False
        return True

    @classmethod
    def get_sorted_directory_paths(cls, directory_path: Path) -> List[Path]:
        cls.sorted_directories_stack = sorted(directory_path.iterdir())
        for directory in cls.sorted_directories_stack:
            if not directory.is_dir():
                continue
        cls.directories_count = len(cls.sorted_directories_stack)
        return cls.sorted_directories_stack

    @classmethod
    def search_for_directories_space(cls, directory_path: Path):
        pass

    @classmethod
    def handle_image_limit(
        cls, number_of_images: int, images_list: List[Path], directory_path: Path
    ) -> None:
        new_directory_name = cls.next_directory_name(DIRECTORY_NAMES)
        LOGGER.info(
            f"Number of images exceeded the maximum limit {MAXIMUM_IMAGE_COUNT_PER_DIRECTORY}"
        )
        LOGGER.info(f"Creating a new directory '{new_directory_name}'")
        new_directory: Path = cls.create_new_directory(
            new_directory_name=new_directory_name,
        )
        cls.move_images_to_new_directory(number_of_images, images_list, new_directory)

    @classmethod
    def next_directory_name(cls, directory_names: List[str]) -> str | None:
        for index, name in enumerate(directory_names):
            if index == cls.directories_count:
                return name

    @classmethod
    def create_new_directory(cls, new_directory_name: str | None) -> Path:
        new_directory_name = cls.next_directory_name(DIRECTORY_NAMES)
        if new_directory_name is None:
            LOGGER.error("Ran out of names")
            return Path()

        new_directory_path: Path = config.ORIGINAL_DIRECTORY_PATH / new_directory_name
        new_directory_path.mkdir(parents=True, exist_ok=True)
        cls.sorted_directories_stack.append(new_directory_path)

        return new_directory_path

    @classmethod
    def move_images_to_new_directory(
        cls, number_of_images: int, images_list: List[Path], new_directory: Path
    ):
        number_of_images_moved: int = 0
        last_image_index: int = -1
        while (
            number_of_images - number_of_images_moved
        ) > MAXIMUM_IMAGE_COUNT_PER_DIRECTORY:
            last_image: Path = images_list[last_image_index]
            last_image.move_into(new_directory)
            number_of_images_moved += 1
            last_image_index -= 1
            images_list.remove(last_image)
        else:
            LOGGER.info(
                f"Moved '{number_of_images_moved}' images to {new_directory.name}"
            )

    @classmethod
    def process_all_directories(cls, directory_path: Path) -> None:
        directories = cls.get_sorted_directory_paths(directory_path)

        from images import Image

        Image.directories_count = cls.directories_count

        for directory in directories:
            LOGGER.info(
                f"Found child directory '{directory.name}' -> Begin rearranging"
            )
            Image.initialize_directory_images(directory)
