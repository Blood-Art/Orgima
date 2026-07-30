from config import LOGGER
import sys
from pathlib import Path
from config import ARGUMENTS
from image_manipulation import ImageManipulator
from directories import Directory
from image_manager import ImageManager
import filetype


class Validator:
    def __init__(self, input_path: Path):
        self.input_path = input_path

    def validate_input(self) -> None:
        if not self.input_path.exists():
            self.log_error("Invalid input no such path exists ❌")
            sys.exit(1)

        if self.input_path == self.input_path.parent:
            confirmation = input(
                "This it the root path, are you sure you want to continue? (y/n)\n"
            )

            if confirmation.lower() != "y":
                return

        if self.input_path.is_dir():
            self.process_directory()
            sys.exit(0)
        elif filetype.is_image(self.input_path):
            self.process_image()
            sys.exit(0)

    def process_image(
        self,
    ) -> None:
        manipulator = ImageManipulator(self.input_path)
        if ARGUMENTS.enable_rounding:
            LOGGER.info("Rounding Image...")
            manipulator.round_image(self.input_path)
            LOGGER.info("Task Finished")
        if ARGUMENTS.enable_upscale:
            LOGGER.info("Upscaling Image...")
            manipulator.upscale_image(self.input_path)
            LOGGER.info("Task Finished")
        if not ARGUMENTS.enable_upscale and not ARGUMENTS.enable_rounding:
            LOGGER.warning(
                "ignoring this action. There wasn't any flag provided for this image. orgima -h for more info."
            )

    def process_directory(self) -> None:
        self.log_flags()
        Directory.ROOT_DIRECTORY = Directory.initialize_directory(self.input_path)
        ImageManager.process_directory_images()

    def log_error(self, message: str):
        LOGGER.error(message)
        LOGGER.info("Exiting...")

    def log_flags(self):
        if ARGUMENTS.include_hidden:
            LOGGER.info("Include hidden directories Enabled ℹ️")

        if not ARGUMENTS.disable_remove_duplicates:
            LOGGER.info("Remove Duplicate non-upscaled images Enabled ℹ️")
