from typing import Callable
from scripts.mo.notion_storage import NotionStorage
from scripts.mo.sqlite_storage import SQLiteStorage
from scripts.mo.storage import Storage

STORAGE_SQLITE = 'SQLite'
STORAGE_NOTION = 'Notion'


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

    def is_storage_initialized(self) -> bool:
        return hasattr(self, 'storage')

    def is_storage_has_errors(self) -> bool:
        return hasattr(self, 'storage_error')


env = Environment()


def _init_notion_storage():
    error = None
    if hasattr(env, 'mo_notion_api_token') and hasattr(env, 'mo_notion_db_id'):
        notion_api_token = env.mo_notion_api_token().strip()
        notion_db_id = env.mo_notion_db_id().strip()

        if notion_api_token and notion_db_id:
            try:
                env.storage = NotionStorage(notion_api_token, notion_db_id)
            except Exception as e:
                error = f'failed to init notion storage: {e}'
        elif not notion_api_token:
            error = "Notion API token is missing"
        else:
            error = "Notion database Id token is missing"

    elif not hasattr(env, 'mo_notion_api_token'):
        error = 'env.mo_notion_api_token attribute not set'
    else:
        error = 'env.mo_notion_db_id attribute not set'
    return error


def _init_sqlite_storage():
    error = None
    try:
        env.storage = SQLiteStorage()
    except Exception as e:
        error = f'failed to init SQLite storage: {e}'
    return error


def initialize_storage():
    error = None
    if hasattr(env, 'mo_storage_type'):
        storage_type = env.mo_storage_type()
        if storage_type == STORAGE_NOTION:
            error = _init_notion_storage()
        elif storage_type == STORAGE_SQLITE:
            error = _init_sqlite_storage()
        else:
            error = f'unknown mo_storage_type attribute value: {storage_type}'
    else:
        env.storage_error = 'mo_storage_type attribute is missing.'

    if error is not None:
        env.storage_error = f'Unable to initialize database: {error}'
