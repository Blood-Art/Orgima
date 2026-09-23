# Orgima

## About
Orgima is a simple CLI tool to organize and process your image or wallpaper library.

## Features
- Detect duplicate images and delete them.
- Rounding images.
- Bulk renaming with an option to modify the Prefix/Suffix of the name.
- Matching images to a set resolution and bulk resizing.
- Upscaling images.
- Grouping, Sorting, Moving images.

## Dependencies
- filetype
- imagehash
- pillow
- (optional) realesrgan-ncnn-vulkan for upscaling.

## Installation
If you want the upscaling feature make sure you have [realesrgan-ncnn-vulkan](https://github.com/xinntao/Real-ESRGAN-ncnn-vulkan) installed.

## Usage
orgima [-h] [-c COUNT] [-i] [-d] [-R] [-r RADIUS] [-p PREFIX] [-s SUFFIX] [-e] [-U] [-u UPSCALE_AMOUNT] [-M] [-m SET_SIZE] [-y] path

Orgima Args:
positional (required) arguments:
  path                  Input Path for a directory or image path to modify.

  | Options:                | Description |
  |  :---                   |   :--- |
  | -h, --help              | show this help message and exit. |
  | -c, --count COUNT       | Set the image count limit per directory. (default: 100). |
  | -i, --include_hidden    | Whether to include hidden directories or not. (default: False). |
  | -d, --remove_duplicates | Whether to check for and remove duplicated/copies of images.(default: False). |
  | -R, --enable_rounding   | Whether to enable rounding images or not. (default: False). |
  | -r, --radius RADIUS     | Set the rounding radius, this is capped at 100. (default: 15). |
  | -p, --prefix PREFIX     | Set a prefix (name before index) for the image/s. |
  | -s, --suffix SUFFIX     | Set a suffix (name after index) for the image/s. |
  | -e, --no_extension      | Don't include the images extension in the renaming process (format) (default: False). |
  | -U, --enable_upscale | Enable image upscaling using the 'realesrgan-ncnn-vulkan' tool (default: False). |
  | -u, --upscale_amount | UPSCALE_AMOUNT | Upscale amount by an integer value (default: 2). |
  | -M, --match_size     | Enable Checking and Matching images scale/size (default: False). |
  | -m, --set_size SET_SIZE | Set the size for matching image Resolution (default: 3840x2160). |
  | -y, --no_prompt | Disable the prompt for Confirmation. (Yes To Everything) (default: False). |

## License
MIT License. See [LICENSE](LICENSE) for details.
