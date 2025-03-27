from abc import ABC, abstractmethod
from typing import Dict, List

from scripts.mo.models import Record, ModelType


def map_dict_to_record(id_, raw: Dict) -> Record:
    return Record(
        id_=id_,
        name=raw['name'],
        model_type=ModelType.by_value(raw['model_type']),
        download_url=raw['download_url'],
        url=raw['url'],
        download_path=raw['download_path'],
        download_filename=raw['download_filename'],
        preview_url=raw['preview_url'],
        description=raw['description'],
        positive_prompts=raw['positive_prompts'],
        negative_prompts=raw['negative_prompts'],
        sha256_hash=raw['sha256_hash'],
        md5_hash=raw['md5_hash'],
        created_at=raw['created_at'],
        groups=raw['groups'],
        subdir=raw['subdir'],
        location=raw['location'],
        weight=raw['weight']
    )


def map_record_to_dict(record: Record) -> dict:
    return {
        'id': record.id_,
        'name': record.name,
        'model_type': record.model_type.value,
        'download_url': record.download_url,
        'url': record.url,
        'download_path': record.download_path,
        'download_filename': record.download_filename,
        'preview_url': record.preview_url,
        'description': record.description,
        'positive_prompts': record.positive_prompts,
        'negative_prompts': record.negative_prompts,
        'sha256_hash': record.sha256_hash,
        'md5_hash': record.md5_hash,
        'created_at': record.created_at,
        'groups': record.groups,
        'subdir': record.subdir,
        'location': record.location,
        "weight": record.weight
    }


class Storage(ABC):

    @abstractmethod
    def get_all_records(self) -> List:
        pass

    @abstractmethod
    def query_records(self, name_query=None, groups=None, model_types=None, show_downloaded=None,
                      show_not_downloaded=None) -> List:
        pass

    @abstractmethod
    def get_record_by_id(self, _id) -> Record:
        pass

    @abstractmethod
    def add_record(self, record: Record):
        pass

    @abstractmethod
    def update_record(self, record: Record):
        pass

    @abstractmethod
    def remove_record(self, _id):
        pass

    @abstractmethod
    def get_available_groups(self) -> List:
        pass

    @abstractmethod
    def get_records_by_group(self, group: str) -> List:
        pass

    @abstractmethod
    def get_all_records_locations(self) -> List:
        pass

    @abstractmethod
    def get_records_by_name(self, record_name) -> List:
        pass

    @abstractmethod
    def get_records_by_url(self, url) -> List:
        pass

    @abstractmethod
    def get_records_by_download_destination(self, download_path, download_filename) -> List:
        pass
