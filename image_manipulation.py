from pathlib import Path


class ImageManipulator:
    images_list: list[Path] = []

    def change_images_extension(self) -> None: ...

    def round_images(self) -> None: ...

    def upscale_images(self) -> None: ...
