from abc import ABC, abstractmethod

from scripts.mo.models import Record


class Repository(ABC):

    @abstractmethod
    def fetch_data(self) -> list[Record]:
        pass

    @abstractmethod
    def fetch_data_by_id(self, _id) -> Record:
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
