import hashlib
import logging
import os.path
from typing import Callable

from scripts.mo.models import ModelType, Record
from scripts.mo.data.storage import Storage

STORAGE_SQLITE = 'SQLite'
STORAGE_FIREBASE = 'Firebase'

LAYOUT_CARDS = 'Cards'
LAYOUT_TABLE = 'Table'

DEFAULT_CARD_WIDTH = 250
DEFAULT_CARD_HEIGHT = 350

_SETTINGS_FILE = 'settings.txt'


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
# logger.setLevel(logging.DEBUG)
logger.setLevel(logging.WARNING)

handler = logging.StreamHandler()
# handler.setLevel(logging.DEBUG)
handler.setLevel(logging.WARNING)

handler.setFormatter(CustomFormatter())

logger.addHandler(handler)


class Environment:
    storage: Storage
    storage_error: str

    storage_type: Callable[[], str]
    download_preview: Callable[[], bool]
    resize_preview: Callable[[], bool]
    nsfw_blur: Callable[[], bool]
    model_path: Callable[[], str]
    vae_path: Callable[[], str]
    lora_path: Callable[[], str]
    hypernetworks_path: Callable[[], str]
    lycoris_path: Callable[[], str]
    embeddings_path: Callable[[], str]
    script_dir: str
    layout: Callable[[], str]
    card_width: Callable[[], str]
    card_height: Callable[[], str]
    is_debug_mode_enabled: Callable[[], bool]

    def is_storage_initialized(self) -> bool:
        return hasattr(self, 'storage')

    def is_storage_has_errors(self) -> bool:
        return hasattr(self, 'storage_error')

    def get_model_path(self, model_type: ModelType):
        if model_type == ModelType.CHECKPOINT:
            path = self.model_path()
        elif model_type == ModelType.VAE:
            path = self.vae_path()
        elif model_type == ModelType.LORA:
            path = self.lora_path()
        elif model_type == model_type.HYPER_NETWORK:
            path = self.hypernetworks_path()
        elif model_type == model_type.LYCORIS:
            path = self.lycoris_path()
        elif model_type == model_type.EMBEDDING:
            path = self.embeddings_path()
        else:
            return None
        return path.strip()

    @staticmethod
    def read_settings():
        path = os.path.join(env.script_dir, _SETTINGS_FILE)
        if not os.path.exists(path):
            return {}

        with open(path) as f:
            lines = f.readlines()

        result = {}
        for line in lines:
            key, value = line.strip().split(': ')
            result[key] = value
            logger.info(f'{key}: {value}')
        logger.info('Settings loaded.')
        return result

    @staticmethod
    def save_settings(settings: dict):
        with open(os.path.join(env.script_dir, _SETTINGS_FILE), 'w') as f:
            for key, value in settings.items():
                f.write(f'{key}: {value}\n')
            logger.info('Settings saved')


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
