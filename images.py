from pathlib import Path
from config import (
    LOGGER,
    IMAGE_EXTENSIONS,
    ARGUMENTS,
)

from directories import Directory
import re


class Image:
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

        for directory in Directory.directories_list:
            LOGGER.info(f"Processing {directory.name}'s images")

        if not ARGUMENTS.disable_remove_duplicates:
            LOGGER.info("Removing Duplicate non-upscaled images Enabled ℹ️")
            for directory in Directory.directories_list:
                cls.remove_upscaled_duplicates(directory)

        for directory in Directory.directories_list:
            LOGGER.info(f"Checking {directory.name}'s image counts")
            Directory.check_directory_image_count(directory)

        for directory in Directory.directories_list:
            cls.rename_images(directory)
            LOGGER.info(f"Images in {directory.name} Organized successfully ✅")
            LOGGER.info("Task Finished")

    @classmethod
    def rename_images(cls, directory: Directory) -> None:
        temp_names_list: list[Path] = cls.set_temp_names(directory)
        for image_index, image in enumerate(temp_names_list):
            image.rename(image.with_stem(f"{image_index + 1}"))

    @classmethod
    def set_temp_names(cls, directory: Directory) -> list[Path]:
        images_list: list[Path] = directory.images_list
        temp_names_list = []
        for image in images_list:
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

        for image in list(images_list):
            if image.stem in upscaled_images_list:
                LOGGER.info(f"Deleted duplicate {image.name} image")
                cls.remove_image_from_directory(directory, image)
                image.unlink(missing_ok=True)

    @classmethod
    def remove_image_from_directory(cls, directory: Directory, image: Path):
        directory.images_list.remove(image)
        directory.image_count -= 1

    @classmethod
    def move_image_to_directory(
        cls, directory: Directory, image: Path, image_destination: Path
    ):
        directory.image_count += 1
        directory.images_moved += 1
        image_moved = image.move(image_destination)
        directory.images_list.append(image_moved)
