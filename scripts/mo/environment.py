from typing import Callable

from scripts.mo.models import ModelType
from scripts.mo.storage import Storage

STORAGE_SQLITE = 'SQLite'
STORAGE_NOTION = 'Notion'

LAYOUT_CARDS = 'Cards'
LAYOUT_TABLE = 'Table'


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
