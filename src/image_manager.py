from pathlib import Path

import filetype
import imagehash
from PIL import Image as PilImage

from config import (
    ARGUMENTS,
    LOGGER,
)
from directories import Directory
from image_manipulation import ImageManipulator


class ImageManager:
    @classmethod
    def process_directory_images(cls) -> None:
        if not ARGUMENTS.disable_remove_duplicates:
            for directory in Directory.directories_list:
                cls.check_duplicate_images(directory)

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
    def check_duplicate_images(cls, directory: Directory) -> None:
        images_list: list[Path] = sorted(directory.images_list)
        phashes_dict: dict[imagehash.ImageHash, str] = {}

        for image in images_list:
            with PilImage.open(image) as img:
                hash: imagehash.ImageHash = imagehash.phash(img)
                if hash not in phashes_dict:
                    phashes_dict[hash] = image.name
                    continue

                original_image_name: str | None = phashes_dict.get(hash)
                LOGGER.info(f"Found Duplicate Image {image.name} with {original_image_name}")
                while True:
                    confirmation: str = input(f"Do you want to delete {image.name}? (y/n) ")
                    if confirmation.lower() == "y" or confirmation == "":
                        image.unlink()
                        directory.remove_image_from_directory(image)
                        LOGGER.info(f"Removed {image.name} successfully")
                        break
                    elif confirmation.lower() == "n":
                        break
