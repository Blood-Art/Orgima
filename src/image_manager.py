import filetype
from image_manipulation import ImageManipulator
from pathlib import Path
from config import (
    LOGGER,
    ARGUMENTS,
)
import re
from directories import Directory


class ImageManager:
    @classmethod
    def process_directory_images(cls) -> None:
        if not ARGUMENTS.disable_remove_duplicates:
            for directory in Directory.directories_list:
                cls.remove_upscaled_duplicates(directory)

        for directory in Directory.directories_list:
            LOGGER.info(f"Checking {directory.name}'s image counts")
            directory.check_directory_image_count()

        for directory in Directory.directories_list:
            cls.rename_images(directory)
            LOGGER.info(f"Images in {directory.name} Organized successfully ✅")
            LOGGER.info("Task Finished")

        for directory in Directory.directories_list:
            manipulator = ImageManipulator(directory)
            if ARGUMENTS.enable_rounding:
                manipulator.round_directory_images()

            if ARGUMENTS.enable_upscale:
                manipulator.scale_directory_images()

    @classmethod
    def rename_images(cls, directory: Directory) -> None:
        temp_names_list: list[Path] = cls.set_temp_names(directory)
        final_names_list: list[Path] = []
        for image_index, image in enumerate(temp_names_list):
            final_image_name: str = (
                f"{ARGUMENTS.prefix}{image_index + 1}{ARGUMENTS.suffix}"
            )
            if not ARGUMENTS.no_extension:
                kind = filetype.guess_extension(image)
                final_image = image.rename(
                    image.with_name(f"{final_image_name}.{kind}")
                )
            else:
                final_image = image.rename(image.with_name(final_image_name))
            final_names_list.append(final_image)
        directory.images_list = final_names_list

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
            if ("upscale") not in image.name:
                continue
            LOGGER.info(f"Found upscaled image '{image.name}'")
            match = re.match(r"^[^_]+", image.name)
            if match:
                upscaled_images_list.append(match.group())

        for image in list(images_list):
            if image.stem in upscaled_images_list:
                LOGGER.info(f"Deleted duplicate {image.name} image")
                directory.move_image_from_directory(image)
                image.unlink(missing_ok=True)

    def remove_duplicates(self, directory: Directory) -> None: ...
