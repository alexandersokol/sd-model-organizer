from notion_client import Client

from scripts.mo.models import Record
from scripts.mo.repository import Repository


def read_title_property(result, name: str):
    try:
        return result["properties"][name]["title"][0]["plain_text"]
    except IndexError:
        return ""


def read_text_property(result, name: str):
    try:
        return result["properties"][name]["rich_text"][0]["text"]["content"]
    except IndexError:
        return ""


def map_result(result):
    id_ = result["id"]
    name = read_title_property(result, "Name")
    type_ = read_text_property(result, "Type")
    url = read_text_property(result, "URL")
    preview_url = read_text_property(result, "PreviewURL")
    download_url = read_text_property(result, "DownloadURL")

    return Record(
        id_=id_,
        name=name,
        model_type=type_,
        url=url,
        preview_url=preview_url,
        download_url=download_url
    )


def map_results(results):
    mapped = []
    for result in results:
        print(result)
        mapped.append(map_result(result))
    return mapped


def prop_title(name: str, value: str):
    return {name: {
        "title": [
            {
                "text": {
                    "content": value
                }
            }
        ]
    }
    }


def prop_text(name: str, value: str):
    return {name: {
        "rich_text": [
            {
                "text": {
                    "content": value
                }
            }
        ]
    }
    }


class NotionRepository(Repository):
    def __init__(self, api_token, database_id):
        self.api_token = api_token
        self.database_id = database_id
        self.notion = Client(auth=api_token)
        self.database = self.notion.databases.retrieve(database_id)

    def fetch_data(self):
        results = self.notion.databases.query(
            **{
                "database_id": self.database_id,
            }
        ).get("results")
        return map_results(results)

    def add_record(self, record: Record):
        return self.notion.pages.create(
            **{
                "parent": {
                    "type": "database_id",
                    "database_id": self.database_id
                },
                "properties": {
                    **prop_title("Name", record.name),
                    **prop_text("Type", record.model_type.value),
                    **prop_text("URL", record.url),
                    **prop_text("DownloadURL", record.download_url),
                    **prop_text("PreviewURL", record.download_url),
                }
            }
        )
