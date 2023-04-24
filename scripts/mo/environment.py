import hashlib
import logging
import os.path
from typing import Callable

from scripts.mo.models import ModelType, Record
from scripts.mo.storage import Storage

STORAGE_SQLITE = 'SQLite'
STORAGE_NOTION = 'Notion'

LAYOUT_CARDS = 'Cards'
LAYOUT_TABLE = 'Table'


class CustomFormatter(logging.Formatter):
    light_green = '\033[92m'
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "[%(levelname)s] %(message)s"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: light_green + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        _formatter = logging.Formatter(log_fmt)
        return _formatter.format(record)


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)

handler.setFormatter(CustomFormatter())

logger.addHandler(handler)


class Environment:
    storage: Storage
    storage_error: str

    mo_storage_type: Callable[[], str]
    mo_notion_api_token: Callable[[], str]
    mo_notion_db_id: Callable[[], str]
    mo_model_path: Callable[[], str]
    mo_vae_path: Callable[[], str]
    mo_lora_path: Callable[[], str]
    mo_hypernetworks_path: Callable[[], str]
    mo_embeddings_path: Callable[[], str]
    mo_script_dir: str
    mo_layout: Callable[[], str]
    mo_card_width: Callable[[], str]
    mo_card_height: Callable[[], str]

    def is_storage_initialized(self) -> bool:
        return hasattr(self, 'storage')

    def is_storage_has_errors(self) -> bool:
        return hasattr(self, 'storage_error')

    def get_model_path(self, model_type: ModelType):
        if model_type == ModelType.CHECKPOINT:
            path = self.mo_model_path()
        elif model_type == ModelType.VAE:
            path = self.mo_vae_path()
        elif model_type == ModelType.LORA:
            path = self.mo_lora_path()
        elif model_type.HYPER_NETWORK:
            path = self.mo_hypernetworks_path()
        elif model_type.EMBEDDING:
            path = self.mo_embeddings_path()
        else:
            return None
        return path.strip()


env = Environment()


def calculate_md5(file_path):
    with open(file_path, 'rb') as f:
        md5 = hashlib.md5()
        while True:
            data = f.read(1024)
            if not data:
                break
            md5.update(data)
    return md5.hexdigest()


def calculate_sha256(file_path):
    with open(file_path, 'rb') as file:
        sha256_hash = hashlib.sha256()
        while chunk := file.read(4096):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()


def find_local_files(record: Record):
    if record.md5_hash:
        if record.download_path:
            model_path = record.download_path
        else:
            model_path = env.get_model_path(record.model_type)

        lookup_dir = os.path.join(model_path, record.subdir)

        model_file_path = None

        if os.path.isdir(lookup_dir):
            files = [f for f in os.listdir(lookup_dir) if os.path.isfile(os.path.join(lookup_dir, f))]
            for file in files:
                file_path = os.path.join(lookup_dir, file)
                file_hash = calculate_md5(file_path)
                if file_hash == record.md5_hash:
                    model_file_path = file_path
                    break

        preview_file_path = None

        if model_file_path is not None:
            filename = os.path.basename(model_file_path)
            extensions = ('.jpeg', '.jpg', '.png', '.webp', '.gif', '.bmp')
            for file in os.listdir(lookup_dir):
                if file.startswith(filename) and file.endswith(extensions):
                    print(os.path.join(lookup_dir, file))

        return [model_file_path, preview_file_path]

    return [None, None]
