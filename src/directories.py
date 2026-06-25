import filetype
from config import (
    MAXIMUM_IMAGE_COUNT_PER_DIRECTORY,
    LOGGER,
    DIRECTORY_NAMES,
    ARGUMENTS,
    IMAGE_EXTENSIONS,
)
from pathlib import Path


class Directory:
    ROOT_DIRECTORY_PATH: Path = Path()
    directories_count: int = 0
    directories_list: list[Directory] = []

    def __init__(
        self,
        path: Path = Path(),
        name: str = "",
        image_count: int = 0,
    ):
        self.path = path
        self.name = name
        self.image_count = image_count
        self.images_moved_count = 0
        self.images_list: list[Path] = []

    @classmethod
    def initialize_directory_objects(cls, directory_path: Path) -> None:
        directory: Directory = Directory(
            path=directory_path,
            name=directory_path.name,
        )

        directory.images_list, directory.image_count = cls.get_sorted_images(
            directory_path
        )

        if directory.is_empty():
            return
        if directory.is_empty_of_images():
            LOGGER.info(
                f"No images were found in [{directory.name}] -> Checking for Child Directories ℹ️"
            )

        if directory.has_child_directories():
            cls.process_child_directories(directory.path)

        if not directory.is_empty_of_images():
            cls.directories_list.append(directory)

    @classmethod
    def process_child_directories(cls, directory_path: Path) -> None:
        child_directories = cls.get_sorted_directory_paths(directory_path)

        for directory in child_directories:
            LOGGER.info(
                f"Found Child Directory '{directory.name}' -> Adding To Queue ➕"
            )
            cls.initialize_directory_objects(directory)

    @classmethod
    def get_sorted_directory_paths(cls, directory_path: Path) -> list[Path]:
        cls.sorted_directories_stack: list[Path] = []

        for directory in sorted(directory_path.iterdir()):
            if not directory.is_dir():
                continue

            if not ARGUMENTS.include_hidden and directory.name.startswith("."):
                continue
            cls.sorted_directories_stack.append(directory)
        cls.directories_count = len(cls.sorted_directories_stack)
        return cls.sorted_directories_stack

    @classmethod
    def create_new_directory(cls) -> Directory:
        new_directory_name: str = cls.get_next_directory_name(DIRECTORY_NAMES)
        new_directory_path: Path = cls.ROOT_DIRECTORY_PATH / new_directory_name
        new_directory_path.mkdir(parents=True, exist_ok=True)
        new_directory: Directory = Directory(
            new_directory_path,
            name=new_directory_name,
        )
        cls.directories_count += 1

        return new_directory

    @classmethod
    def get_next_directory_name(cls, directory_names: tuple[str, ...]) -> str:
        return directory_names[cls.directories_count]

    def find_free_directory(self) -> Directory:

        if Directory.all_directories_full():
            free_directory: Directory = self.create_new_directory()
            LOGGER.warning("All directories are full... ⚠️")
            LOGGER.info(f"Created new directory '{free_directory.name}' ℹ️")
            self.directories_list.append(free_directory)
            return free_directory

        for directory in self.directories_list:
            if directory.is_free():
                return directory
        raise RuntimeError("No free directory found — this should never happen")

    @classmethod
    def all_directories_full(cls) -> bool:

        available_directories: list[Directory] = cls.directories_list
        full_directories: list[Directory] = [
            directory
            for directory in available_directories
            if directory.is_full() or directory.is_over_full()
        ]
        return len(full_directories) == len(available_directories)

    def check_directory_image_count(self) -> None:
        if self.is_over_full():
            LOGGER.warning(
                f"{self.name} has passed the limit of '{MAXIMUM_IMAGE_COUNT_PER_DIRECTORY}' images ⚠️"
            )
            LOGGER.info("Freeing up some space...")
        else:
            LOGGER.info(f"{self.name} has sufficient space ✅")

        while self.is_over_full():
            self.free_up_directory()

    def free_up_directory(self) -> None:

        free_directory: Directory = self.find_free_directory()
        last_image: Path = self.images_list[-1]
        image_destination: Path = (
            free_directory.path
            / f"moved_{free_directory.image_count + 1}{last_image.suffix}"
        )
        self.remove_image_from_directory(last_image)
        self.move_image_to_directory(free_directory, last_image, image_destination)

    def remove_image_from_directory(self, image: Path):
        self.images_list.remove(image)
        self.image_count -= 1

    def move_image_to_directory(
        self, new_directory: Directory, image: Path, image_destination: Path
    ):
        new_directory.image_count += 1
        new_directory.images_moved_count += 1
        image_moved = image.move(image_destination)
        new_directory.images_list.append(image_moved)

    @classmethod
    def get_sorted_images(cls, root_directory_path: Path) -> tuple[list[Path], int]:
        images_list: list[Path] = [
            image
            for image in root_directory_path.iterdir()
            if image.is_file() and filetype.is_image(image)
        ]

        # """ Accept only images """
        # for image in root_directory_path.iterdir():
        #     if not filetype.is_image(image) and not image.is_file():
        #         continue
        #     images_list.append(image)
        #
        # images_list = [
        #     image
        #     for image in root_directory_path.iterdir()
        #     if image.is_file() and filetype.is_image(image)
        # ]
        number_of_images: int = len(images_list)

        return sorted(
            images_list, key=lambda img: Path(img).stat().st_ctime
        ), number_of_images

    def is_free(self) -> bool:
        return self.image_count < MAXIMUM_IMAGE_COUNT_PER_DIRECTORY

    def is_full(self) -> bool:
        return self.image_count == MAXIMUM_IMAGE_COUNT_PER_DIRECTORY

    def is_over_full(self) -> bool:
        return self.image_count > MAXIMUM_IMAGE_COUNT_PER_DIRECTORY

    def is_empty_of_images(self) -> bool:
        return self.image_count == 0

    def is_empty(self) -> bool:
        return not any(self.path.iterdir())

    def has_child_directories(self) -> bool:
        return any(child.is_dir() for child in self.path.iterdir())
