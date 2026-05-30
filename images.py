from typing import List
from pathlib import Path
from config import (
    LOGGER,
    IMAGE_EXTENSIONS,
    MAXIMUM_IMAGE_COUNT_PER_DIRECTORY,
)

from directories import Directory
import re


class Image:
    directories_count: int = 0
    directory_path: Path = Path()

    @classmethod
    def arrange_images(cls, directory_path: Path) -> None:
        if not Directory.directory_exists(cls.directory_path):
            return

        cls.directory_path = directory_path
        images_list: List[Path] = cls.get_sorted_images(directory_path)

        if not images_list:
            LOGGER.info(
                f"No images were found in '{cls.directory_path.name}' -> Checking for child directories"
            )
            Directory.process_all_directories(cls.directory_path)
            return

        cls.remove_upscaled_duplicates(images_list)
        temp_names_list = cls.set_temp_names(images_list)
        for idx, image in enumerate(temp_names_list):
            image.rename(image.with_stem(str(idx + 1)))

        LOGGER.info("Task Finished")

    @classmethod
    def get_sorted_images(cls, directory_path: Path) -> List[Path]:
        images_list: List[Path] = []

        """ Accept only images """
        for image in Path.iterdir(directory_path):
            if image.suffix not in IMAGE_EXTENSIONS:
                continue
            images_list.append(image)

        number_of_images = len(images_list)

        if number_of_images > 0:
            LOGGER.info(
                f"Found '{number_of_images}' images in {cls.directory_path.name}"
            )

        if number_of_images > MAXIMUM_IMAGE_COUNT_PER_DIRECTORY:
            Directory.handle_image_limit(number_of_images, images_list, directory_path)

        return sorted(images_list, key=lambda img: Path(img).stat().st_ctime)

    @classmethod
    def set_temp_names(cls, images_list: List[Path]) -> List[Path]:
        temp_names_list = []
        for image in images_list:
            temp_name = image.rename(cls.directory_path / f"temp_{image.name}")
            temp_names_list.append(temp_name)

        return temp_names_list

    @classmethod
    def remove_upscaled_duplicates(cls, images_list: List[Path]) -> None:
        upscaled_images_list = []
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
