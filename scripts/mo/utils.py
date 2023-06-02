import datetime
import hashlib
import json
import os
import re
import urllib.parse
from typing import List

from PIL import Image

from scripts.mo.environment import env

_HASH_CACHE_FILENAME = 'hash_cache.json'

MODEL_EXTENSIONS = ['.bin', '.ckpt', '.safetensors', '.pt']
PREVIEW_EXTENSIONS = [".png", ".jpg", ".webp"]


def is_blank(s: str) -> bool:
    """
    Checks string is empty or contains only whitespaces.
    :param s: String to check.
    :return: True if string is empty or contains only whitespaces.
    """
    return len(s.strip()) == 0


def is_valid_url(url: str) -> bool:
    """
    Checks url is valid.
    :param url: url string to validate.
    :return: True if url is valid.
    """
    parsed_url = urllib.urlparse.urlparse(url)
    return parsed_url.scheme in ['http', 'https']


def is_valid_filename(filename: str) -> bool:
    """
    Checks filename is valid.
    :param filename: string to validate.
    :return: True if filename is valid.
    """
    pattern = re.compile(r'^[^\x00-\x1f\\/?*:|"<>]+$')
    return bool(pattern.match(filename))


def get_model_files_in_dir(lookup_dir: str) -> List:
    """
    Scans for model files in the lookup_dir, and it's child directories.
    :param lookup_dir: directory path to scan.
    :return: List of models in the directory and subdirectories.
    """
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
    """
    Extracts filename without extension for models.
    :param model_file: model filename string.
    :return: model filename without extension.
    """
    filename = os.path.basename(model_file)
    for ext in MODEL_EXTENSIONS:
        if filename.endswith(ext):
            return filename[:-len(ext)]
    return filename


def find_preview_file(model_file_path):
    """
    Looks for model image preview.
    :param model_file_path: path to model file.
    :return: path to model image preview if it exists, None otherwise.
    """
    if model_file_path:
        filename_no_ext = get_model_filename_without_extension(model_file_path)
        path = os.path.join(os.path.dirname(model_file_path), filename_no_ext)

        potential_files = sum([[path + ext, path + ".preview" + ext] for ext in PREVIEW_EXTENSIONS], [])

        for file in potential_files:
            if os.path.isfile(file):
                return file

    return None


def find_info_file(model_file_path):
    """
    Looks for model info file.
    :param model_file_path: path to model file.
    :return: path to model info file if exists, None otherwise.
    """
    if model_file_path:
        filename_no_ext = get_model_filename_without_extension(model_file_path)
        potential_file = os.path.join(os.path.dirname(model_file_path), filename_no_ext, '.info')

        return potential_file if os.path.exists(potential_file) else None

    return None


def link_preview(preview_path):
    """
    Creates link for model image preview file. File should be in one of the model supported directories.
    :param preview_path: path to model preview.
    :return: link to model preview image.
    """
    return "./sd_extra_networks/thumb?filename=" + urllib.parse.quote(preview_path.replace('\\', '/')) + "&mtime=" + \
        str(os.path.getmtime(preview_path))


def resize_preview_image(input_file, output_file):
    """
    Resizes input image to fit model card size.
    :param input_file: input image file path.
    :param output_file: output image file path.
    :return: None
    """
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


def calculate_file_temp_hash(file_path):
    """
    Calculates file "temp" hash. This has is based on file creation and modification timestamps and file size.
    This is using to determinate file was changed or not.
    :param file_path: path to target file.
    :return: md5 hex digest string.
    """
    creation_timestamp = os.path.getctime(file_path)
    creation_datetime = datetime.datetime.fromtimestamp(creation_timestamp)

    modification_timestamp = os.path.getmtime(file_path)
    modification_datetime = datetime.datetime.fromtimestamp(modification_timestamp)

    size = os.path.getsize(file_path)

    input_string = f'{creation_datetime} {modification_datetime} {size}'

    md5_hash = hashlib.md5()
    md5_hash.update(input_string.encode('utf-8'))
    return md5_hash.hexdigest()


def calculate_sha256(file_path):
    """
    Calculates SHA256 file hash.
    :param file_path: target file path.
    :return: SHA256 hex digest string.
    """
    with open(file_path, 'rb') as file:
        sha256_hash = hashlib.sha256()
        while chunk := file.read(4096):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()


def get_hash_cache_file():
    """
    Returns hash cache file path.
    :return: string file path.
    """
    return os.path.join(env.script_dir, _HASH_CACHE_FILENAME)


def read_hash_cache() -> List:
    """
    Reads hash cache file data.
    :return: hash cache data as a list of dictionaries.
    """
    file_path = get_hash_cache_file()
    if os.path.isfile(file_path):
        with open(file_path) as file:
            return json.load(file)
    return []


def write_hash_cache(hash_cache: List):
    """
    Writes hash cache data to file.
    :param hash_cache: list of dictionaries to save.
    :return: None.
    """
    with open(get_hash_cache_file(), 'w') as file:
        json.dump(hash_cache, file, indent=4)
