import os
import sqlite3
import threading
import time

from scripts.mo.models import Record, ModelType
from scripts.mo.storage import Storage
from scripts.mo.environment import env

_DB_FILE = 'database.sqlite'
_DB_VERSION = 3
_DB_TIMEOUT = 30


def map_row_to_record(row) -> Record:
    return Record(
        id_=row[0],
        name=row[1],
        model_type=ModelType.by_value(row[2]),
        download_url=row[3],
        url=row[4],
        download_path=row[5],
        download_filename=row[6],
        preview_url=row[7],
        description=row[8],
        positive_prompts=row[9],
        negative_prompts=row[10],
        model_hash=row[11],
        md5_hash=row[12],
        created_at=row[13],
        groups=row[14].split(",")
    )


class SQLiteStorage(Storage):

    def __init__(self):
        self.local = threading.local()
        self._initialize()

    def _connection(self):
        if not hasattr(self.local, "connection"):
            db_file_path = os.path.join(env.mo_script_dir, _DB_FILE)
            self.local.connection = sqlite3.connect(db_file_path, _DB_TIMEOUT)
        return self.local.connection

    def _initialize(self):
        cursor = self._connection().cursor()

        cursor.execute('''CREATE TABLE IF NOT EXISTS Record
                                    (id INTEGER PRIMARY KEY,
                                    _name TEXT,
                                    model_type TEXT,
                                    download_url TEXT,
                                    url TEXT DEFAULT '',
                                    download_path TEXT DEFAULT '',
                                    download_filename TEXT DEFAULT '',
                                    preview_url TEXT DEFAULT '',
                                    description TEXT DEFAULT '',
                                    positive_prompts TEXT DEFAULT '',
                                    negative_prompts TEXT DEFAULT '',
                                    model_hash TEXT DEFAULT '',
                                    md5_hash TEXT DEFAULT '',
                                    created_at INTEGER DEFAULT 0,
                                    groups TEXT DEFAULT '')
                                 ''')

        cursor.execute(f'''CREATE TABLE IF NOT EXISTS Version
                                (version INTEGER DEFAULT {_DB_VERSION})''')
        # cursor.execute("INSERT INTO Version VALUES (1)")  # insert initial version value
        # TODO version check
        self._connection().commit()
        self._check_database_version()

    def _check_database_version(self):
        cursor = self._connection().cursor()
        cursor.execute('SELECT * FROM Version ', )
        row = cursor.fetchone()

        if row is None:
            cursor.execute(f'INSERT INTO Version VALUES ({_DB_VERSION})')
            self._connection().commit()

        version = _DB_VERSION if row is None else row[0]
        if version != _DB_VERSION:
            self._run_migration(version)

    def _run_migration(self, current_version):
        if current_version == 1 and _DB_VERSION == 2:
            self._migrate_1_to_2()
            current_version = 2

        if current_version == 2 and _DB_VERSION == 3:
            self._migrate_2_to_3()

    def _migrate_1_to_2(self):
        cursor = self._connection().cursor()
        cursor.execute('ALTER TABLE Record ADD COLUMN created_at INTEGER DEFAULT 0;')
        cursor.execute("DELETE FROM Version")
        cursor.execute('INSERT INTO Version VALUES (2)')
        self._connection().commit()

    def _migrate_2_to_3(self):
        cursor = self._connection().cursor()
        cursor.execute("ALTER TABLE Record ADD COLUMN groups TEXT DEFAULT '';")
        cursor.execute("DELETE FROM Version")
        cursor.execute('INSERT INTO Version VALUES (3)')
        self._connection().commit()

    def get_all_records(self) -> list[Record]:
        cursor = self._connection().cursor()
        cursor.execute('SELECT * FROM Record')
        rows = cursor.fetchall()
        result = []
        for row in rows:
            result.append(map_row_to_record(row))
        return result

    def get_record_by_id(self, id_) -> Record:
        cursor = self._connection().cursor()
        cursor.execute('SELECT * FROM Record WHERE id=?', (id_,))
        row = cursor.fetchone()
        return None if row is None else map_row_to_record(row)

    def get_records_by_group(self, group: str) -> list[Record]:
        cursor = self._connection().cursor()
        cursor.execute(f"SELECT * FROM Record WHERE LOWER(groups) LIKE '%{group}%'")
        rows = cursor.fetchall()
        result = []
        for row in rows:
            result.append(map_row_to_record(row))
        return result

    def add_record(self, record: Record):
        cursor = self._connection().cursor()
        data = (
            record.name,
            record.model_type.value,
            record.download_url,
            record.url,
            record.download_path,
            record.download_filename,
            record.preview_url,
            record.description,
            record.positive_prompts,
            record.negative_prompts,
            record.model_hash,
            record.md5_hash,
            time.time(),
            ",".join(record.groups)
        )
        cursor.execute(
            """INSERT INTO Record(
                    _name,
                    model_type,
                    download_url,
                    url,
                    download_path,
                    download_filename,
                    preview_url,
                    description,
                    positive_prompts,
                    negative_prompts,
                    model_hash,
                    md5_hash,
                    created_at,
                    groups) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            data)
        self._connection().commit()

    def update_record(self, record: Record):
        cursor = self._connection().cursor()
        data = (
            record.name,
            record.model_type.value,
            record.download_url,
            record.url,
            record.download_path,
            record.download_filename,
            record.preview_url,
            record.description,
            record.positive_prompts,
            record.negative_prompts,
            record.model_hash,
            record.md5_hash,
            ",".join(record.groups),
            record.id_
        )
        cursor.execute(
            """UPDATE Record SET 
                    _name=?,
                    model_type=?,
                    download_url=?,
                    url=?,
                    download_path=?,
                    download_filename=?,
                    preview_url=?,
                    description=?,
                    positive_prompts=?,
                    negative_prompts=?,
                    model_hash=?,
                    md5_hash=?,
                    groups=?
                WHERE id=?
            """, data
        )

        self._connection().commit()

    def remove_record(self, _id):
        cursor = self._connection().cursor()
        cursor.execute("DELETE FROM Record WHERE id=?", (_id,))
        self._connection().commit()

    def get_available_groups(self) -> list[str]:
        cursor = self._connection().cursor()
        cursor.execute('SELECT groups FROM Record')
        rows = cursor.fetchall()
        result = []
        for row in rows:
            result.extend(row[0].split(","))

        result = list(set(result))
        return list(filter(None, result))
