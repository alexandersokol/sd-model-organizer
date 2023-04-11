import sqlite3

from scripts.mo.models import Record, ModelType
from scripts.mo.storage import Storage

db_file = 'database.sqlite'
db_version = 1
db_timeout = 30


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
        md5_hash=row[12]
    )


class SQLiteStorage(Storage):
    def __init__(self):
        self.connection = sqlite3.connect(db_file, db_timeout)
        cursor = self.connection.cursor()

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
                            md5_hash TEXT DEFAULT '')
                         ''')

        cursor.execute(f'''CREATE TABLE IF NOT EXISTS Version
                        (version INTEGER DEFAULT {db_version})''')
        # cursor.execute("INSERT INTO Version VALUES (1)")  # insert initial version value
        # TODO version check
        self.connection.commit()

    def fetch_data(self) -> list[Record]:
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM Record')
        rows = cursor.fetchall()
        result = []
        for row in rows:
            result.append(map_row_to_record(row))
        return result

    def fetch_data_by_id(self, id_) -> Record:
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM Record WHERE id=?', (id_,))
        row = cursor.fetchone()
        return None if row is None else map_row_to_record(row)

    def add_record(self, record: Record):
        cursor = self.connection.cursor()
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
            record.md5_hash
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
                    md5_hash) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            data)
        self.connection.commit()

    def update_record(self, record: Record):
        cursor = self.connection.cursor()
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
                    md5_hash=?
                WHERE id=?
            """, data
        )

        self.connection.commit()

    def remove_record(self, _id):
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM Record WHERE id=?", (_id,))
        self.connection.commit()
