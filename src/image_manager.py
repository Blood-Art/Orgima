import sys
from pathlib import Path
from re import search

import filetype
import imagehash
from PIL import Image as PilImage

import config
import utils
from config import (
    ARGUMENTS,
    LOGGER,
)
from directories import Directory
from image_manipulation import ImageManipulator
from utils import confirmation


class ImageManager:
    @classmethod
    def process_directory_images(cls) -> None:
        cls.remove_dir_duplicates()
        cls.match_dir_sizes()
        cls.check_dir_counts()
        cls.rename_dir_images()
        cls.manipulate_dir_images()

    @classmethod
    def remove_dir_duplicates(cls) -> None:
        if ARGUMENTS.remove_duplicates:
            for directory in Directory.directories_list:
                utils.time_function(cls.check_duplicate_images, directory)

    @classmethod
    def match_dir_sizes(cls) -> None:
        if ARGUMENTS.match_size:
            for directory in Directory.directories_list:
                utils.time_function(cls.check_image_sizes, directory)

    @classmethod
    def check_dir_counts(cls) -> None:
        for directory in Directory.directories_list:
            LOGGER.info(f"Checking {directory.name}'s image counts")
            directory.check_directory_image_count()

    @classmethod
    def rename_dir_images(cls) -> None:
        for directory in Directory.directories_list:
            cls.rename_images(directory)
            LOGGER.info(f"Images in {directory.name} Organized successfully ✅")
            LOGGER.info("Task Finished")

    @classmethod
    def manipulate_dir_images(cls) -> None:
        for directory in Directory.directories_list:
            manipulator = ImageManipulator(directory)
            if ARGUMENTS.enable_rounding:
                utils.time_function(manipulator.round_directory_images)
            if ARGUMENTS.enable_upscale:
                utils.time_function(manipulator.scale_directory_images)

    @classmethod
    def rename_images(cls, directory: Directory) -> None:
        temp_names_list: list[Path] = cls.set_temp_names(directory)
        final_names_list: list[Path] = []
        for index, image in enumerate(temp_names_list):
            final_name: str = f"{ARGUMENTS.prefix}{index + 1}{ARGUMENTS.suffix}"
            final_image: Path = cls.get_image_extension(image, final_name)
            final_names_list.append(final_image)
        directory.images_list = final_names_list

    @classmethod
    def set_temp_names(cls, directory: Directory) -> list[Path]:
        """Takes a directory as input, loop through it's image_list, rename each image -> Returns a list of temporary names."""

        images_list: list[Path] = directory.images_list
        temp_names_list = []
        for image in images_list:
            utils.check_for_hidden_image(image)
            temp_name: Path = image.rename(directory.path / f"temp_{image.name}")
            temp_names_list.append(temp_name)
        directory.images_list = temp_names_list
        return temp_names_list

    @classmethod
    def get_image_extension(cls, image: Path, final_name: str) -> Path:
        if not ARGUMENTS.no_extension:
            kind = filetype.guess_extension(image)
            final_image = image.rename(image.with_name(f"{final_name}.{kind}"))
        else:
            final_image = image.rename(image.with_name(final_name))
        return final_image

    @classmethod
    def check_duplicate_images(cls, directory: Directory) -> None:
        images_list: list[Path] = sorted(directory.images_list)
        phashes_dict: dict[imagehash.ImageHash, Path] = {}
        for image in images_list:
            with PilImage.open(image) as img:
                hash: imagehash.ImageHash = imagehash.phash(img)
                if hash not in phashes_dict:
                    phashes_dict[hash] = image
                    continue

                original_image: Path | None = phashes_dict.get(hash)
                if isinstance(original_image, Path):
                    LOGGER.info(
                        f"Found Duplicate Image {image.parent.name}/{image.name} with {original_image.parent.name}/{original_image.name}"
                    )
                cls.ask_for_deletion(image, directory)

    @classmethod
    def ask_for_deletion(cls, image: Path, directory: Directory) -> None:
        response = confirmation(message="Do you want to Delete {image.parent.name}/{image.name}?")
        if response:
            image.unlink()
            if directory.name == image.parent.name:
                directory.remove_image_from_directory(image)
            Directory.all_directory_images.remove(image)
            LOGGER.info(f"Removed {image.name} Successfully")

    @classmethod
    def check_image_sizes(cls, directory: Directory) -> None:
        if config.MATCH_IMAGE_SIZE != config.DEFAULT_MATCH_SIZE:
            requested_size = cls.parse_resolution_string()
        else:
            requested_size = utils.convert_str_resolution_to_tuple(config.DEFAULT_MATCH_SIZE)

        for image in directory.images_list:
            with PilImage.open(image) as img:
                if img.size == requested_size:
                    continue
                LOGGER.info(f"{image.name} is not of size {requested_size}")
                message: str = f"Do you want to scale this image to {requested_size}?"
                response: bool = confirmation(message)
                if response:
                    origial_path = image.joinpath(image.parent, image.name)
                    resized_image = img.resize(requested_size)
                    resized_image.save(origial_path)

    @classmethod
    def parse_resolution_string(cls, match_size_string: str = config.MATCH_IMAGE_SIZE) -> tuple[int, int]:
        match = search(r"\b\d{3,4}[xX]\d{3,4}\b", match_size_string)
        if not match:
            LOGGER.error(
                "Size Match is not Correct. Make sure it's in the format WxH Where W is the width and H is the height of the image."
            )
            sys.exit(1)

        width, height = utils.convert_str_resolution_to_tuple(match.group())

        return (width, height)
