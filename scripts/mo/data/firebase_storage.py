import os.path

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from google.cloud.firestore_v1 import CollectionReference

from scripts.mo.data.storage import Storage
from scripts.mo.environment import env
from scripts.mo.models import Record, ModelType


def _map_dict_to_record(id_, raw: dict) -> Record:
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
        location=raw['location']
    )


def _map_record_to_dict(record: Record) -> dict:
    return {
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
        'location': record.location
    }


def _filter_download(record: Record, show_downloaded, show_not_downloaded):
    is_downloaded = bool(record.location) and os.path.exists(record.location)
    return (show_downloaded and is_downloaded) or (show_not_downloaded and not is_downloaded)


class FirebaseStorage(Storage):

    def __init__(self):
        cred = credentials.Certificate(os.path.join(env.mo_script_dir, "service-account-file.json"))
        self.app = firebase_admin.initialize_app(cred)
        self.firestore_client = firestore.client()

    def _records(self) -> CollectionReference:
        return self.firestore_client.collection('records')

    def get_all_records(self) -> list[Record]:
        record_refs = self._records().stream()
        records = []
        for ref in record_refs:
            records.append(_map_dict_to_record(ref.id, ref.to_dict()))
        return records

    def query_records(self, name_query=None, groups=None, model_types=None, show_downloaded=None,
                      show_not_downloaded=None) -> list[Record]:

        query_ref = self._records()
        if model_types is not None and model_types:
            query_ref = query_ref.where('model_type', 'in', model_types)

        records = []
        for ref in query_ref.stream():
            records.append(_map_dict_to_record(ref.id, ref.to_dict()))

        if name_query is not None and name_query:
            records = [record for record in records if name_query.lower() in record.name.lower()]

        if groups is not None and len(groups) > 0:
            records = [item for item in records if all(val in item.groups for val in groups)]

        records = list(filter(lambda r: _filter_download(r, show_downloaded, show_not_downloaded), records))

        return records

    def get_record_by_id(self, _id) -> Record:
        doc = self._records().document(_id).get()
        return _map_dict_to_record(doc.id, doc.to_dict())

    def add_record(self, record: Record):
        self._records().add(_map_record_to_dict(record))

    def update_record(self, record: Record):
        ref = self._records().document(record.id_)
        ref.update(_map_record_to_dict(record))

    def remove_record(self, _id):
        self._records().document(_id).delete()

    def get_available_groups(self) -> list[str]:
        records = self.get_all_records()
        groups = []
        for record in records:
            if len(record.groups) > 0:
                groups.extend(record.groups)
        return list(set(groups))

    def get_records_by_group(self, group: str) -> list[Record]:
        col_ref = self._records()

        query_ref = col_ref.where('group', 'array_contains', f'%{group}%')

        records = []
        for ref in query_ref.stream():
            records.append(_map_dict_to_record(ref.id, ref.to_dict()))
        return records

    def get_all_records_locations(self) -> list[str]:
        records = self.get_all_records()
        locations = []
        for record in records:
            if record.location:
                locations.append(record.location)
        return list(set(locations))
