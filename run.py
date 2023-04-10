# from sqlite_repository import SQLiteRepository
from scripts.src.models import Record
from scripts.src.notion_repository import NotionRepository

# db = SQLiteRepository("/content/default.sqlite")
# print(db.fetchData())
db = NotionRepository("", "")
records = db.fetch_data()
for record in records:
    print(record)

response = db.add_record(
    Record(
        id_="",
        name="YAE MIKKO",
        type_="CHECKPOINT",
        url="https://url.link",
        download_url="https://downloadUrl.link",
        preview_url="https://previewUrl.link"
    )
)

print(response)
