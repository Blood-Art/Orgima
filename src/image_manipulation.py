import filetype
from directories import Directory
from pathlib import Path
from PIL import Image as PilImage, ImageDraw
from config import RADIUS, LOGGER, MAXIMUM_IMAGE_COUNT_PER_DIRECTORY
from time import perf_counter
from concurrent.futures import ProcessPoolExecutor
from config import UPSCALE_AMOUNT, TOOLS_ARGUMENTS, IMAGE_EXTENSIONS
import subprocess
import sys


class ImageManipulator:
    SCALING_FACTOR: int = 1000
    RADIUS_MAGNITUDE: int = 10

    def __init__(self, input: Path | Directory):
        self.input = input

    def initialize_rounding(self, input: Path | Directory) -> None:
        self.RADIUS = min(RADIUS, 100)
        if not isinstance(input, Directory):
            self.rounded_directory_path: Path = input.parent
            return
        self.directory = input
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
        self.initialize_rounding(self.input)
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
            kind = filetype.guess_extension(image_path)
            output_path: Path = image_path.with_name(
                f"{image_path.stem}_scaled_{UPSCALE_AMOUNT}x.{kind}"
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

            self.downscale_image(output_path)

        except subprocess.CalledProcessError as e:
            LOGGER.error(f"Error: {e}")
            sys.exit(1)
        except FileNotFoundError:
            LOGGER.error(
                "Error: realesrgan-ncnn-vulkan was not found in path, make sure it is installed."
            )

    def downscale_image(self, output_path: Path):
        with PilImage.open(output_path) as img:
            scaled_img_size: tuple[int, int] = (
                int(img.width * (UPSCALE_AMOUNT / 4)),
                int(img.height * (UPSCALE_AMOUNT / 4)),
            )
            new_format = img.format
            print(new_format)
            if "-f" in TOOLS_ARGUMENTS:
                format_index = TOOLS_ARGUMENTS.index("-f") + 1
                new_format = TOOLS_ARGUMENTS[format_index]
                output_path = output_path.with_suffix(f".{new_format}")
                print("Changing format...")

            resized_image = img.resize(scaled_img_size, PilImage.Resampling.LANCZOS)
            new_format = new_format.upper() if new_format is not None else new_format
            resized_image.save(output_path, format=new_format)

    def scale_directory_images(self) -> None:
        LOGGER.info(
            f"Scaling {self.directory.image_count} images in {self.directory.name}, UPSCALE_AMOUNT: {UPSCALE_AMOUNT}"
        )
        start = perf_counter()
        with ProcessPoolExecutor() as executor:
            executor.map(self.upscale_image, self.directory.images_list)
        end = perf_counter()
        LOGGER.info(f"it took {end - start:0.2f} seconds to finish upscaling")
