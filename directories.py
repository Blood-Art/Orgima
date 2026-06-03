from config import MAXIMUM_IMAGE_COUNT_PER_DIRECTORY, LOGGER, DIRECTORY_NAMES, ARGUMENTS
from pathlib import Path


class Directory:
    ROOT_DIRECTORY_PATH: Path = Path()
    directories_count: int = 0
    free_directories_list: list[Directory] = []

    def __init__(
        self,
        path: Path = Path(),
        name: str = "",
        image_count: int = 0,
        images_moved: int = 0,
        images_list: list[  # <- Make sure to initialize to make a copy
            Path
        ] = [],
    ):
        self.path = path
        self.name = name
        self.image_count = image_count
        self.images_moved = images_moved
        self.images_list = images_list

    @classmethod
    def log_directory_error(cls, message: str):
        LOGGER.error(message)
        LOGGER.info("Exiting...")

    @classmethod
    def process_all_directories(cls, directory_path: Path) -> None:
        directories = cls.get_sorted_directory_paths(directory_path)

        from images import Image

        for directory in directories:
            LOGGER.info(
                f"Found Child Directory '{directory.name}' -> Adding To Queue ➕"
            )
            Image.initalize_directory_objects(directory)

    @classmethod
    def get_sorted_directory_paths(cls, directory_path: Path) -> list[Path]:
        cls.sorted_directories_stack: list[Path] = []

        for directory in sorted(directory_path.iterdir()):
            if not directory.is_dir():
                continue

            if not ARGUMENTS.hidden and directory.name.startswith("."):
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
            images_list=[],
        )
        cls.directories_count += 1
        # cls.sorted_directories_stack.append(new_directory_path)

        return new_directory

    @classmethod
    def get_next_directory_name(cls, directory_names: list[str]) -> str:
        new_name: str = ""
        for index, name in enumerate(directory_names):
            if index == cls.directories_count:
                new_name = name
        return new_name

    @classmethod
    def find_free_directory(cls, directories: list[Directory]) -> Directory:
        from images import Image

        free_directory: Directory = Directory()
        for directory in directories:
            if directory.is_free() and directory not in cls.free_directories_list:
                free_directory = directory
                cls.free_directories_list.append(free_directory)

            if directory.is_free():
                free_directory = directory

        if cls.all_directories_full():
            free_directory = cls.create_new_directory()
            LOGGER.warning("All directories are full... ⚠️")
            LOGGER.info(f"Created new directory '{free_directory.name}' ℹ️")
            Image.directory_list.append(free_directory)
            cls.free_directories_list.append(free_directory)
        return free_directory

    @classmethod
    def all_directories_full(cls) -> bool:
        from images import Image

        available_directories: list[Directory] = Image.directory_list
        full_directories: list[Directory] = []
        for directory in available_directories:
            if directory.is_full() or directory.is_pass_count_limit():
                full_directories.append(directory)
        return full_directories == available_directories

    def log_images_moved(self):
        LOGGER.info(f"Moved {self.images_moved} images to {self.name} ↩️")

    def is_free(self) -> bool:
        return self.image_count < MAXIMUM_IMAGE_COUNT_PER_DIRECTORY

    def is_full(self) -> bool:
        return self.image_count == MAXIMUM_IMAGE_COUNT_PER_DIRECTORY

    def is_pass_count_limit(self) -> bool:
        return self.image_count > MAXIMUM_IMAGE_COUNT_PER_DIRECTORY

    def contains(self, image: Path) -> bool:
        return image in self.path.iterdir()

    def is_empty_of_images(self) -> bool:
        return self.image_count == 0

    def is_empty(self) -> bool:
        return next(self.path.iterdir(), None) is None
