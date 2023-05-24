import os
import re
import urllib.parse

from PIL import Image

from scripts.mo.environment import env

model_extensions = ['.bin', '.ckpt', '.safetensors', '.pt']
preview_extensions = [".png", ".jpg", ".webp"]


def is_blank(s):
    return len(s.strip()) == 0


def is_valid_url(url: str) -> bool:
    pattern = re.compile(r'^https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+')
    return bool(pattern.match(url))


def is_valid_filename(filename: str) -> bool:
    pattern = re.compile(r'^[^\x00-\x1f\\/?*:|"<>]+$')
    return bool(pattern.match(filename))


def get_model_files_in_dir(lookup_dir: str) -> list[str]:
    root_dir = os.path.join(lookup_dir, '')
    extensions = ('.bin', '.ckpt', '.safetensors', '.pt')
    result = []

    if os.path.isdir(root_dir):
        for subdir, dirs, files in os.walk(root_dir):
            for file in files:
                ext = os.path.splitext(file)[-1].lower()
                if ext in extensions:
                    filepath = os.path.join(subdir, file)
                    result.append(filepath)
    return result


def get_model_filename_without_extension(model_file):
    filename = os.path.basename(model_file)
    for ext in model_extensions:
        if filename.endswith(ext):
            return filename[:-len(ext)]
    return filename


def find_preview_file(model_file):
    if model_file:
        filename_no_ext = get_model_filename_without_extension(model_file)
        path = os.path.join(os.path.dirname(model_file), filename_no_ext)

        potential_files = sum([[path + ext, path + ".preview" + ext] for ext in preview_extensions], [])

        for file in potential_files:
            if os.path.isfile(file):
                return file

    return None


def link_preview(filename):
    return "./sd_extra_networks/thumb?filename=" + urllib.parse.quote(filename.replace('\\', '/')) + "&mtime=" + \
        str(os.path.getmtime(filename))


def resize_preview_image(input_file, output_file):
    image = Image.open(input_file)

    desired_width = int(env.card_width() * 1.5)
    desired_height = int(env.card_height() * 1.5)

    aspect_ratio = image.width / image.height

    desired_aspect_ratio = desired_width / desired_height

    if aspect_ratio > desired_aspect_ratio:
        new_width = int(desired_height * aspect_ratio)
        new_height = desired_height
    else:
        new_width = desired_width
        new_height = int(desired_width / aspect_ratio)

    resized_image = image.resize((new_width, new_height), Image.LANCZOS)

    canvas = Image.new("RGB", (desired_width, desired_height))

    x_position = (desired_width - new_width) // 2
    y_position = (desired_height - new_height) // 2

    canvas.paste(resized_image, (x_position, y_position))

    canvas.save(output_file, "JPEG")
