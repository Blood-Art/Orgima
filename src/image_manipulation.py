from directories import Directory
from pathlib import Path
from PIL import Image as PilImage, ImageDraw
from config import RADIUS, LOGGER, MAXIMUM_IMAGE_COUNT_PER_DIRECTORY
from time import perf_counter
from concurrent.futures import ProcessPoolExecutor


class ImageManipulator:
    SCALING_FACTOR: int = 1000
    RADIUS_MAGNITUDE: int = 10

    def __init__(self, input: Path | Directory):
        self.initialize_rounding(input)

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
        LOGGER.info(
            f"Rounding {self.directory.image_count} images in {self.directory.name}, Radius: {self.RADIUS}"
        )
        start = perf_counter()
        with ProcessPoolExecutor() as executor:
            executor.map(self.round_image, self.directory.images_list)
        end = perf_counter()
        LOGGER.info(f"it took {end - start:0.2f} seconds to finish rounding")

    def change_images_extension(self) -> None: ...

    def upscale_images(self) -> None: ...
