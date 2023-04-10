from scripts.src.repository import Repository


class SQLiteRepository(Repository):

    def __init__(self, db_path):
        self.dbPath = db_path

    def fetch_data(self):
        return "SQLite Data"

    def add_record(self, record):
        pass
