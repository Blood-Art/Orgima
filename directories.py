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
        images_move_count: int = 0,
        images_list: list[  # <- Make sure to initialize to make a copy
            Path
        ] = [],
    ):
        self.path = path
        self.name = name
        self.image_count = image_count
        self.images_moved_count = images_move_count
        self.images_list = images_list

    @classmethod
    def initalize_directory_objects(cls, directory_path: Path) -> None:
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

        # if directory.path is not directory.ROOT_DIRECTORY_PATH:
        #     cls.directories_list.append(directory)
        if directory.has_child_directories():
            cls.process_child_directories(directory.path)

        if not directory.is_empty_of_images():
            cls.directories_list.append(directory)

    @classmethod
    def log_directory_error(cls, message: str):
        LOGGER.error(message)
        LOGGER.info("Exiting...")

    @classmethod
    def process_child_directories(cls, directory_path: Path) -> None:
        child_directories = cls.get_sorted_directory_paths(directory_path)

        for directory in child_directories:
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
            if directory.is_full() or directory.is_over_full():
                full_directories.append(directory)
        return full_directories == available_directories

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
        else:
            self.post_free_up_directory()

    def free_up_directory(self) -> None:
        from images import Image

        free_directory = Directory.find_free_directory(self.directories_list)
        last_image: Path = self.images_list[-1]
        image_destination: Path = (
            free_directory.path
            / f"moved_{free_directory.image_count + 1}{last_image.suffix}"
        )
        Image.remove_image_from_directory(self, last_image)
        Image.move_image_to_directory(free_directory, last_image, image_destination)

    def post_free_up_directory(self) -> None:
        if self.is_full():
            self.log_images_moved()
        Directory.free_directories_list.clear()

    def log_images_moved(self) -> None:
        for free_directory in Directory.free_directories_list:
            LOGGER.info(
                f"Moved {free_directory.images_moved_count} images to {self.name} ↩️"
            )

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
