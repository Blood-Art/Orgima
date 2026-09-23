#!/usr/bin/env python3
from pathlib import Path

from config import ARGUMENTS
from validation import Validator


def main():
    input = Path(ARGUMENTS.path)
    validator = Validator(input)
    validator.validate_input()


if __name__ == "__main__":
    main()
