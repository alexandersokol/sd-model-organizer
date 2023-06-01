import os.path
from typing import List

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from google.cloud.firestore_v1 import CollectionReference

from scripts.mo.data.storage import Storage, map_dict_to_record, map_record_to_dict
from scripts.mo.environment import env
from scripts.mo.models import Record


def _filter_download(record: Record, show_downloaded, show_not_downloaded):
    is_downloaded = bool(record.location) and os.path.exists(record.location)
    return (show_downloaded and is_downloaded) or (show_not_downloaded and not is_downloaded)


class FirebaseStorage(Storage):

    def __init__(self):
        cred = credentials.Certificate(os.path.join(env.script_dir, "service-account-file.json"))
        self.app = firebase_admin.initialize_app(cred)
        self.firestore_client = firestore.client()

    def _records(self) -> CollectionReference:
        return self.firestore_client.collection('records')

    def get_all_records(self) -> List:
        record_refs = self._records().stream()
        records = []
        for ref in record_refs:
            records.append(map_dict_to_record(ref.id, ref.to_dict()))
        return records

    def query_records(self, name_query=None, groups=None, model_types=None, show_downloaded=None,
                      show_not_downloaded=None) -> List:

        query_ref = self._records()
        if model_types is not None and model_types:
            query_ref = query_ref.where('model_type', 'in', model_types)

        records = []
        for ref in query_ref.stream():
            records.append(map_dict_to_record(ref.id, ref.to_dict()))

        if name_query is not None and name_query:
            records = [record for record in records if name_query.lower() in record.name.lower()]

        if groups is not None and len(groups) > 0:
            records = [item for item in records if all(val in item.groups for val in groups)]

        records = list(filter(lambda r: _filter_download(r, show_downloaded, show_not_downloaded), records))

        return records

    def get_record_by_id(self, _id) -> Record:
        doc = self._records().document(_id).get()
        return map_dict_to_record(doc.id, doc.to_dict())

    def add_record(self, record: Record):
        self._records().add(map_record_to_dict(record))

    def update_record(self, record: Record):
        ref = self._records().document(record.id_)
        ref.update(map_record_to_dict(record))

    def remove_record(self, _id):
        self._records().document(_id).delete()

    def get_available_groups(self) -> List:
        records = self.get_all_records()
        groups = []
        for record in records:
            if len(record.groups) > 0:
                groups.extend(record.groups)
        return list(set(groups))

    def get_records_by_group(self, group: str) -> List:
        col_ref = self._records()

        query_ref = col_ref.where('group', 'array_contains', f'%{group}%')

        records = []
        for ref in query_ref.stream():
            records.append(map_dict_to_record(ref.id, ref.to_dict()))
        return records

    def get_all_records_locations(self) -> List:
        records = self.get_all_records()
        locations = []
        for record in records:
            if record.location:
                locations.append(record.location)
        return list(set(locations))
