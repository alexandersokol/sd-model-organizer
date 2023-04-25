from abc import ABC, abstractmethod

from scripts.mo.models import Record


class Storage(ABC):

    @abstractmethod
    def get_all_records(self) -> list[Record]:
        pass

    @abstractmethod
    def query_records(self, name_query=None, groups=None, model_types=None, show_downloaded=None,
                      show_not_downloaded=None) -> list[Record]:
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
    def get_available_groups(self) -> list[str]:
        pass

    @abstractmethod
    def get_records_by_group(self, group: str) -> list[Record]:
        pass
