from scripts.mo.environment import env, STORAGE_SQLITE
from scripts.mo.data.sqlite_storage import SQLiteStorage


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

        if storage_type == STORAGE_SQLITE:
            error = _init_sqlite_storage()
        else:
            error = f'unknown mo_storage_type attribute value: {storage_type}'
    else:
        env.storage_error = 'mo_storage_type attribute is missing.'

    if error is not None:
        env.storage_error = f'Unable to initialize database: {error}'
