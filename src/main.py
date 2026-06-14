#!/usr/bin/env python
from pathlib import Path
from config import ARGUMENTS
from validation import Validator


def main():
    input = Path(ARGUMENTS.path)
    validatior = Validator(input)
    validatior.validate_input()


if __name__ == "__main__":
    main()
