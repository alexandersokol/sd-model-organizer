from scripts.mo.environment import env, STORAGE_SQLITE, STORAGE_FIREBASE


def _init_sqlite_storage():
    error = None
    try:
        from scripts.mo.data.sqlite_storage import SQLiteStorage
        env.storage = SQLiteStorage()
    except Exception as e:
        error = f'failed to init SQLite storage: {e}'
    return error


def _init_firebase_storage():
    error = None
    try:
        from scripts.mo.data.firebase_storage import FirebaseStorage
        env.storage = FirebaseStorage()
    except Exception as e:
        error = f'failed to init Firebase storage: {e}'
    return error


def initialize_storage():
    error = None
    if hasattr(env, 'storage_type'):
        storage_type = env.storage_type()

        if storage_type == STORAGE_SQLITE:
            error = _init_sqlite_storage()
        elif storage_type == STORAGE_FIREBASE:
            error = _init_firebase_storage()
        else:
            error = f'unknown storage_type attribute value: {storage_type}'
    else:
        env.storage_error = 'storage_type attribute is missing.'

    if error is not None:
        env.storage_error = f'Unable to initialize database: {error}'
