from config import MAXIMUM_IMAGE_COUNT_PER_DIRECTORY, LOGGER, DIRECTORY_NAMES, ARGUMENTS
from pathlib import Path


class Directory:
    ROOT_DIRECTORY_PATH: Path = Path()
    directories_count: int = 0
    directories_list: list[Directory] = []
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
    def initalize_directory_objects(cls, directory_path: Path) -> None:
        if not directory_path.is_dir():
            return
        directory: Directory = Directory(
            path=directory_path,
            name=directory_path.name,
        )

        from images import Image

        directory.images_list, directory.image_count = Image.get_sorted_images(
            directory_path
        )

        if directory.is_empty():
            return
        if directory.is_empty_of_images():
            LOGGER.info(
                f"No images were found in [{directory.name}] -> Checking for Child Directories ℹ️"
            )
            cls.process_all_directories(directory.ROOT_DIRECTORY_PATH)

        if directory.path is not directory.ROOT_DIRECTORY_PATH:
            cls.directories_list.append(directory)

    @classmethod
    def log_directory_error(cls, message: str):
        LOGGER.error(message)
        LOGGER.info("Exiting...")

    @classmethod
    def process_all_directories(cls, directory_path: Path) -> None:
        directories = cls.get_sorted_directory_paths(directory_path)

        for directory in directories:
            LOGGER.info(
                f"Found Child Directory '{directory.name}' -> Adding To Queue ➕"
            )
            cls.initalize_directory_objects(directory)

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
            images_list=[],
        )
        cls.directories_count += 1

        return new_directory

    @classmethod
    def get_next_directory_name(cls, directory_names: tuple[str, ...]) -> str:
        new_name: str = ""
        for index, name in enumerate(directory_names):
            if index == cls.directories_count:
                new_name = name
        return new_name

    @classmethod
    def find_free_directory(cls, directories: list[Directory]) -> Directory:

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
            cls.directories_list.append(free_directory)
            cls.free_directories_list.append(free_directory)
        return free_directory

    @classmethod
    def all_directories_full(cls) -> bool:

        available_directories: list[Directory] = cls.directories_list
        full_directories: list[Directory] = []
        for directory in available_directories:
            if directory.is_full() or directory.is_pass_count_limit():
                full_directories.append(directory)
        return full_directories == available_directories

    @classmethod
    def check_directory_image_count(cls, directory: Directory) -> None:
        if directory.is_pass_count_limit():
            LOGGER.warning(
                f"{directory.name} has passed the limit of '{MAXIMUM_IMAGE_COUNT_PER_DIRECTORY}' images ⚠️"
            )
            LOGGER.info("Freeing up some space...")
        else:
            LOGGER.info(f"{directory.name} has sufficient space ✅")

        for image in list(directory.images_list):
            if directory.is_pass_count_limit():
                cls.free_up_directory(directory, image)

    @classmethod
    def free_up_directory(cls, current_directory: Directory, image: Path) -> None:
        from images import Image

        free_directory = Directory.find_free_directory(cls.directories_list)
        image_destination = (
            free_directory.path
            / f"moved_{free_directory.image_count + 1}{image.suffix}"
        )

        Image.remove_image_from_directory(current_directory, image)
        Image.move_image_to_directory(free_directory, image, image_destination)
        if current_directory.is_full():
            for free_directory in Directory.free_directories_list:
                free_directory.log_images_moved()
        Directory.free_directories_list.clear()

    def log_images_moved(self) -> None:
        LOGGER.info(f"Moved {self.images_moved} images to {self.name} ↩️")

    def is_free(self) -> bool:
        return self.image_count < MAXIMUM_IMAGE_COUNT_PER_DIRECTORY

    def is_full(self) -> bool:
        return self.image_count == MAXIMUM_IMAGE_COUNT_PER_DIRECTORY

    def is_pass_count_limit(self) -> bool:
        return self.image_count > MAXIMUM_IMAGE_COUNT_PER_DIRECTORY

    def is_empty_of_images(self) -> bool:
        return self.image_count == 0

    def is_empty(self) -> bool:
        return next(self.path.iterdir(), None) is None
