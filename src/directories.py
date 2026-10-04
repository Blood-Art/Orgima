from pathlib import Path
from typing import ClassVar

from filetype import is_image

from config import (
    ARGUMENTS,
    DIRECTORY_NAMES,
    LOGGER,
    MAXIMUM_IMAGE_COUNT_PER_DIRECTORY,
)


class Directory:
    ROOT_DIRECTORY: Directory | None = None
    directories_list: ClassVar = []
    all_directory_images: ClassVar = []

    def __init__(
        self,
        path: Path,
        name: str,
    ):
        self.path: Path = path
        self.name: str = name
        self.image_count: int = 0
        self.images_list: list[Path] = []
        self.child_directories: list[Directory] = []

    @classmethod
    def initialize_directory(cls, directory_path: Path) -> Directory:
        directory: Directory = Directory(
            path=directory_path,
            name=directory_path.name,
        )
        cls.log_directory_state(directory)
        cls.directories_list.append(directory)
        directory.process_child_directories()
        directory.images_list = directory.get_sorted_images()
        cls.all_directory_images.extend(directory.images_list)
        directory.image_count = directory.get_image_count()
        return directory

    def log_directory_state(self):
        if self.is_empty():
            LOGGER.info(f"{self.name} is empty...")
        elif self.is_empty_of_images():
            LOGGER.info(f"No images were found in [{self.name}] -> Checking for Child Directories ℹ️")
        if not self.is_empty():
            return

    def get_sorted_images(self) -> list[Path]:
        images_list: list[Path] = [image for image in self.path.iterdir() if image.is_file() and is_image(image)]

        return sorted(images_list, key=lambda img: Path(img).stat().st_ctime)

    def get_image_count(self) -> int:
        return len(self.images_list)

    def process_child_directories(self) -> None:
        child_directory_path_list: list[Path] = self.get_child_directory_paths()
        for child in child_directory_path_list:
            LOGGER.info(f"Found Child Directory '{child.name}' -> Adding To Queue ➕")
            child_directory = self.initialize_directory(child)
            self.child_directories.append(child_directory)

    def get_child_directory_paths(self) -> list[Path]:
        child_directory_paths: list[Path] = []
        for child in sorted(self.path.iterdir()):
            if not child.is_dir():
                continue
            if not ARGUMENTS.include_hidden and child.name.startswith("."):
                continue
            child_directory_paths.append(child)
        return child_directory_paths

    def check_directory_image_count(self) -> None:
        if self.is_over_full():
            LOGGER.warning(f"{self.name} has passed the limit of '{MAXIMUM_IMAGE_COUNT_PER_DIRECTORY}' images ⚠️")
            LOGGER.info("Freeing up some space...")

        if self.is_over_full():
            while not self.is_empty_of_images():
                self.free_up_directory()

    def free_up_directory(self) -> None:
        free_directory: Directory = self.find_free_directory()
        last_image: Path = self.images_list[-1]
        image_destination: Path = free_directory.path / f"moved_{free_directory.image_count + 1}{last_image.suffix}"
        self.remove_image_from_directory(last_image)
        self.move_image_to_directory(free_directory, last_image, image_destination)

    def find_free_directory(self) -> Directory:
        for directory in self.child_directories:
            if directory.is_free():
                return directory

        if self.all_child_directories_full():
            created_directory = self.create_new_directory()
            self.directories_list.append(created_directory)
            LOGGER.info(f"Created new directory : {created_directory.name}")
            return created_directory
        raise RuntimeError("No free directory found — this should never happen")

    def all_child_directories_full(self) -> bool:
        available_directories: list[Directory] = self.child_directories
        full_directories: list[Directory] = [
            directory for directory in available_directories if directory.is_full() or directory.is_over_full()
        ]
        return len(full_directories) == len(available_directories)

    def create_new_directory(self) -> Directory:
        new_directory_name: str = self.get_next_directory_name(DIRECTORY_NAMES)
        new_directory_path: Path = self.path / new_directory_name
        new_directory_path.mkdir(parents=True, exist_ok=True)
        new_directory: Directory = Directory(
            path=new_directory_path,
            name=new_directory_name,
        )
        self.child_directories.append(new_directory)

        return new_directory

    def get_next_directory_name(self, directory_names: tuple[str, ...]) -> str:
        """Exclude Root Path"""
        return directory_names[len(self.directories_list) - 1]

    def remove_image_from_directory(self, image: Path):
        self.images_list.remove(image)
        self.image_count -= 1

    def move_image_to_directory(self, new_directory: Directory, image: Path, image_destination: Path):
        new_directory.image_count += 1
        image_moved: Path = image.move(image_destination)
        new_directory.images_list.append(image_moved)

    def is_free(self) -> bool:
        return self.image_count < MAXIMUM_IMAGE_COUNT_PER_DIRECTORY

    def is_full(self) -> bool:
        return self.image_count == MAXIMUM_IMAGE_COUNT_PER_DIRECTORY

    def is_over_full(self) -> bool:
        return self.image_count > MAXIMUM_IMAGE_COUNT_PER_DIRECTORY

    def is_empty_of_images(self) -> bool:
        return not any(image for image in self.path.iterdir() if image.is_file() and is_image(image))

    def is_empty(self) -> bool:
        return not any(self.path.iterdir())
