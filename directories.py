"""Import config file for MAXIMUM_IMAGE_COUNT_PER_DIRECTORY to update across files"""

from config import (
    MAXIMUM_IMAGE_COUNT_PER_DIRECTORY,
    LOGGER,
    DIRECTORY_NAMES,
)
from pathlib import Path


class Directory:
    sorted_directories_stack: list[Path] = []
    directories_count: int = 0
    root_directory_path: Path

    def __init__(
        self,
        path: Path,
        name: str = "",
        image_count: int = 0,
        images_moved: int = 0,
        images_list: list[Path] | None = None,
    ):
        self.path = path
        self.name = name
        self.image_count = image_count
        self.images_moved = images_moved
        self.images_list = images_list

    @classmethod
    def log_missing_directory(cls):
        LOGGER.error("Invalid input no such path exists")
        LOGGER.info("Exiting...")

    @classmethod
    def process_all_directories(cls, directory_path: Path) -> None:
        directories = cls.get_sorted_directory_paths(directory_path)

        from images import Image

        Image.directories_count = cls.directories_count

        for directory in directories:
            LOGGER.info(f"Found Child Directory '{directory.name}' -> Adding To Queue")
            Image.initialize_directory_images(directory)

    @classmethod
    def get_sorted_directory_paths(cls, directory_path: Path) -> list[Path]:
        cls.sorted_directories_stack = sorted(directory_path.iterdir())
        for directory in cls.sorted_directories_stack:
            if not directory.is_dir():
                continue
        cls.directories_count = len(cls.sorted_directories_stack)
        return cls.sorted_directories_stack

    @classmethod
    def next_directory_name(cls, directory_names: list[str]) -> str | None:
        for index, name in enumerate(directory_names):
            if index == cls.directories_count:
                return name

    @classmethod
    def create_new_directory(cls, new_directory_name: str | None) -> Path:
        new_directory_name = cls.next_directory_name(DIRECTORY_NAMES)
        if new_directory_name is None:
            LOGGER.error("Ran out of names")
            return Path()

        new_directory_path: Path = cls.root_directory_path / new_directory_name
        new_directory_path.mkdir(parents=True, exist_ok=True)
        cls.sorted_directories_stack.append(new_directory_path)

        return new_directory_path

    @classmethod
    def find_free_directory(cls, directories: list[Directory]) -> Directory | None:
        for directory in directories:
            if cls.is_directory_free(directory):
                return directory

    @classmethod
    def is_directory_free(cls, directory: Directory) -> bool:
        return directory.image_count < MAXIMUM_IMAGE_COUNT_PER_DIRECTORY

    @classmethod
    def is_directory_full(cls, directory: Directory) -> bool:
        return directory.image_count == MAXIMUM_IMAGE_COUNT_PER_DIRECTORY

    @classmethod
    def is_directory_pass_limit(cls, directory: Directory) -> bool:
        return directory.image_count > MAXIMUM_IMAGE_COUNT_PER_DIRECTORY

    def contains(self, image: Path) -> bool:
        return image in self.path.iterdir()
