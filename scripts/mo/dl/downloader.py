import threading
from abc import ABC, abstractmethod


class Downloader(ABC):
    @abstractmethod
    def accepts_url(self, url: str) -> bool:
        pass

    @abstractmethod
    def fetch_filename(self, url: str):
        pass

    @abstractmethod
    def download(self, url: str, destination_file: str, description: str, stop_event: threading.Event):
        pass

    @abstractmethod
    def check_url_available(self, url: str):
        pass
