from config import ARGUMENTS
from pathlib import Path
from config import (
    LOGGER,
    IMAGE_EXTENSIONS,
    MAXIMUM_IMAGE_COUNT_PER_DIRECTORY,
)

from directories import Directory
import re


class Image:
    directory_list: list[Directory] = []

    @classmethod
    def initalize_directory_objects(cls, directory_path: Path) -> None:
        if not directory_path.is_dir():
            return
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
            Directory.process_all_directories(directory.ROOT_DIRECTORY_PATH)

        """ Exclude Root Directory """
        if directory.path is not directory.ROOT_DIRECTORY_PATH:
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
    def process_directory_images(cls) -> None:
        for directory in cls.directory_list:
            LOGGER.info(f"Processing {directory.name}'s images")
            LOGGER.info(f"Checking {directory.name}'s image counts")
            cls.check_directory_image_count(directory)

        for directory in cls.directory_list:
            cls.rename_images(directory)
            LOGGER.info(f"Images in {directory.name} Organized successfully ✅")
            LOGGER.info("Task Finished")

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
                cls.move_images_to_free_directory(directory, image)

    @classmethod
    def move_images_to_free_directory(
        cls, current_directory: Directory, image: Path
    ) -> None:
        free_directory = Directory.find_free_directory(cls.directory_list)
        image_destination = (
            free_directory.path
            / f"moved_{free_directory.image_count + 1}{image.suffix}"
        )

        current_directory.image_count -= 1
        current_directory.images_list.remove(image)
        free_directory.images_moved += 1
        free_directory.image_count += 1
        image_moved = image.move(image_destination)
        free_directory.images_list.append(image_moved)
        """ Log every image moved when it no longer passes the directory limit i.e becomes 'full' """
        if current_directory.is_full():
            for free_directory in Directory.free_directories_list:
                free_directory.log_images_moved()
        Directory.free_directories_list.clear()

    @classmethod
    def rename_images(cls, directory: Directory) -> None:
        temp_names_list: list[Path] = cls.set_temp_names(directory)
        for image_index, image in enumerate(temp_names_list):
            image.rename(image.with_stem(f"{image_index + 1}"))

    @classmethod
    def set_temp_names(cls, directory: Directory) -> list[Path]:
        images_list: list[Path] = directory.images_list
        temp_names_list = []
        for image in list(images_list):
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
