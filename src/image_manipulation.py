import filetype
from directories import Directory
from pathlib import Path
from PIL import Image as PilImage, ImageDraw
from config import RADIUS, LOGGER, MAXIMUM_IMAGE_COUNT_PER_DIRECTORY
from time import perf_counter
from concurrent.futures import ProcessPoolExecutor
from config import UPSCALE_AMOUNT, TOOLS_ARGUMENTS
import subprocess
import sys


class ImageManipulator:
    SCALING_FACTOR: int = 1000
    RADIUS_MAGNITUDE: int = 10

    def __init__(self, input: Path | Directory):
        self.input = input
        self.RADIUS = min(RADIUS, 100)
        PilImage.MAX_IMAGE_PIXELS = 400_000_000
        if isinstance(input, Directory):
            return
        if filetype.is_image(input):
            self.rounded_directory_path = self.input.parent

    def initialize_rounding_directory(self) -> None:
        if isinstance(self.input, Directory):
            self.directory: Directory = self.input
            rounded_directory_image_count: int = self.directory.image_count * 2
            self.rounded_directory_path: Path = self.directory.path
            if rounded_directory_image_count > MAXIMUM_IMAGE_COUNT_PER_DIRECTORY:
                self.rounded_directory_path = self.directory.path / "rounded"
                self.rounded_directory_path.mkdir(parents=True, exist_ok=True)

    def round_image(self, image_path: Path) -> None:
        with PilImage.open(image_path) as img:
            proportional_radius: int = int(
                (min(img.size) / self.SCALING_FACTOR)
                * (self.RADIUS * self.RADIUS_MAGNITUDE)
            )
            mask = PilImage.new(mode="L", size=img.size)
            draw = ImageDraw.Draw(mask)
            draw.rounded_rectangle(
                xy=[(0, 0), img.size], radius=proportional_radius, fill=255
            )
            self.save_rounded_image(img, mask, image_path)

    def save_rounded_image(
        self, image: PilImage.Image, mask: PilImage.Image, image_path: Path
    ) -> None:
        rounded_image = PilImage.new(mode="RGBA", size=image.size, color=(0, 0, 0, 0))
        rounded_image.paste(im=image, mask=mask)
        rounded_image_path: Path = (
            self.rounded_directory_path / f"{image_path.stem}_rounded.png"
        )
        rounded_image.save(
            rounded_image_path,
            format="PNG",
        )

    def round_directory_images(self) -> None:
        self.initialize_rounding_directory()
        LOGGER.info(
            f"Rounding {self.directory.image_count} images in {self.directory.name}, Radius: {self.RADIUS}"
        )
        start = perf_counter()
        with ProcessPoolExecutor() as executor:
            executor.map(self.round_image, self.directory.images_list)
        end = perf_counter()
        LOGGER.info(f"it took {end - start:0.2f} seconds to finish rounding")

    def upscale_image(self, image_path: Path) -> None:
        try:
            format = filetype.guess_extension(image_path)
            if "-f" in TOOLS_ARGUMENTS:
                format_index = TOOLS_ARGUMENTS.index("-f") + 1
                format = TOOLS_ARGUMENTS[format_index].lower()
                print("Changing format...")

            output_path: Path = image_path.with_name(
                f"{image_path.stem}_scaled_{UPSCALE_AMOUNT}x.{format}"
            )
            subprocess.run(
                [
                    "realesrgan-ncnn-vulkan",
                    "-i",
                    f"{image_path}",
                    "-o",
                    f"{output_path}",
                    "-n",
                    "realesrgan-x4plus-anime",
                ]
                + TOOLS_ARGUMENTS,
                check=True,
            )

            """ The Default Upscale Amount for the x4plus-anime model is x4 so we divide by 4 """
            self.downscale_image(output_path, format)

        except subprocess.CalledProcessError as e:
            LOGGER.error(f"Error: {e}")
            sys.exit(1)
        except FileNotFoundError:
            LOGGER.error(
                "Error: realesrgan-ncnn-vulkan was not found in path, make sure it is installed."
            )
            sys.exit(1)

    def downscale_image(self, output_path: Path, format: str):
        with PilImage.open(output_path) as img:
            scaled_img_size: tuple[int, int] = (
                int(img.width * (UPSCALE_AMOUNT / 4)),
                int(img.height * (UPSCALE_AMOUNT / 4)),
            )
            resized_image = img.resize(scaled_img_size, PilImage.Resampling.LANCZOS)
            if format.lower() == "jpg":
                format: str = "jpeg"
            format = format.upper()
            resized_image.save(output_path, format=format)

    def scale_directory_images(self) -> None:
        LOGGER.info(
            f"Scaling {self.directory.image_count} images in {self.directory.name}, UPSCALE_AMOUNT: {UPSCALE_AMOUNT}"
        )
        start = perf_counter()
        with ProcessPoolExecutor() as executor:
            executor.map(self.upscale_image, self.directory.images_list)
        end = perf_counter()
        LOGGER.info(f"it took {end - start:0.2f} seconds to finish upscaling")
