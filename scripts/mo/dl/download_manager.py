import hashlib
import os
import queue
import shutil
import tempfile
import threading
import traceback
from urllib.parse import urlparse
from copy import deepcopy

from scripts.mo.dl.downloader import Downloader
from scripts.mo.dl.gdrive_downloader import GDriveDownloader
from scripts.mo.dl.http_downloader import HttpDownloader
from scripts.mo.dl.mega_downloader import MegaDownloader
from scripts.mo.environment import env
from scripts.mo.models import Record

GENERAL_STATUS_IN_PROGRESS = 'In Progress'
GENERAL_STATUS_CANCELLED = 'Cancelled'
GENERAL_STATUS_ERROR = 'Error'
GENERAL_STATUS_COMPLETED = 'Completed'

STATE_PENDING = 'Pending'
STATE_IN_PROGRESS = 'In Progress'
STATE_COMPLETED = 'Completed'
STATE_EXISTS = 'Exists'
STATE_ERROR = 'Error'


def _get_destination_file_path(filename: str, record: Record) -> str:
    path = record.download_path
    if not path:
        path = env.get_model_path(record.model_type)
        if path is None:
            raise Exception(f'Destination path is undefined.')

    if not os.path.isdir(path):
        os.makedirs(path)

    return os.path.join(path, record.subdir, filename)


def _get_filename_from_url(url):
    parsed_url = urlparse(url)
    path = parsed_url.path

    filename = os.path.basename(path)
    filename_parts = os.path.splitext(filename)
    filename = filename_parts[0]
    extension = filename_parts[1]

    if extension == '' or extension == '.':
        return None

    return filename + extension


def _get_filename(downloader: Downloader, record: Record) -> str:
    if record.download_filename:
        filename = record.download_filename
    else:
        url_filename = _get_filename_from_url(record.download_url)
        if url_filename is not None:
            return url_filename
        filename = downloader.fetch_filename(record.download_url)
        if filename is None:
            filename = str(record.id_)
    return filename


def _get_preview_extension(url):
    extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
    for ext in extensions:
        if url.endswith(ext):
            return ext
    return 'png'


def _change_file_extension(filename, new_extension):
    base, ext = os.path.splitext(filename)
    if not ext:
        # If the filename has no extension, simply append the new one
        new_filename = base + '.' + new_extension
    else:
        # If the filename has an extension, replace it with the new one
        new_filename = base + '.' + new_extension.lstrip('.')
    return new_filename


def _get_preview_filename(url, filename):
    extension = _get_preview_extension(url)
    return _change_file_extension(filename, extension)


def _calculate_md5(file_path):
    with open(file_path, 'rb') as f:
        md5 = hashlib.md5()
        while True:
            data = f.read(1024)
            if not data:
                break
            md5.update(data)
    return md5.hexdigest()


def _calculate_sha256(file_path):
    with open(file_path, 'rb') as file:
        sha256_hash = hashlib.sha256()
        while chunk := file.read(4096):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()


class DownloadManager:
    __instance = None
    __lock = threading.Lock()

    def __init__(self):
        self._stop_event = threading.Event()
        self._stop_event.set()

        self._state = {}
        self._latest_state = {}
        self._thread = None

        self._downloaders: list[Downloader] = [
            GDriveDownloader(),
            MegaDownloader(),
            HttpDownloader()  # Should always be the last one to give a chance for other http schemas
        ]

    @staticmethod
    def instance():
        if DownloadManager.__instance is None:
            with DownloadManager.__lock:
                if DownloadManager.__instance is None:
                    DownloadManager.__instance = DownloadManager()
        return DownloadManager.__instance

    def is_running(self) -> bool:
        return not self._stop_event.is_set()

    def get_state(self) -> dict:
        return self._state

    def get_latest_state(self) -> dict:
        return self._latest_state

    def start_download(self, records: list[Record]):
        if not self._stop_event.is_set():
            print('Download already running')
            return

        self._stop_event.clear()
        self._state = {}
        self._latest_state = {}
        self._state_update(general_status=GENERAL_STATUS_IN_PROGRESS)
        self._thread = threading.Thread(target=self._download_loop, args=(records,))
        self._thread.start()

    def stop_download(self):
        if self._stop_event.is_set():
            print('Download not running')
            return

        self._stop_event.set()
        self._thread.join()

    def _state_update(self, general_status=None, exception=None, record_id=None, record_state=None):
        new_general_state = deepcopy(self._state)

        latest_state = {}

        if general_status is not None:
            new_general_state['general_status'] = general_status
            latest_state['general_status'] = general_status

        if exception is not None:
            new_general_state['exception'] = str(exception)
            latest_state['exception'] = str(exception)

        if record_id is not None and record_state is not None:
            if new_general_state.get('records') is None:
                new_general_state['records'] = {}

            if new_general_state['records'].get(record_id) is None:
                new_general_state['records'][record_id] = record_state
            else:
                new_general_state['records'][record_id].update(record_state)

            latest_state['records'] = {record_id: record_state}

        self._state = new_general_state
        self._latest_state = latest_state

    def _download_loop(self, records: list[Record]):
        try:
            for record in records:
                for upd in self._download_record(record):
                    self._state_update(record_id=record.id_, record_state=upd)

                    if self._stop_event.is_set():
                        self._state_update(general_status=GENERAL_STATUS_CANCELLED)
                        return

            has_errors = False
            for key, value in self._state['records'].items():
                if value.get('exception') is not None:
                    has_errors = True
                    break

            if has_errors:
                self._state_update(general_status=GENERAL_STATUS_ERROR)
            else:
                self._state_update(general_status=GENERAL_STATUS_COMPLETED)
                # TODO add error into main state

        except Exception as ex:
            self._state_update(general_status=GENERAL_STATUS_ERROR, exception=str(ex))
            traceback.print_exc()

        self._stop_event.set()
        self._running = False

    def _download_record(self, record: Record):
        try:
            yield {'state': STATE_IN_PROGRESS}

            downloader = self._get_downloader(record.download_url)
            print('Start download record with id: ', record.id_)

            filename = _get_filename(downloader, record)
            print('filename: ', filename)

            yield {'filename': filename}

            destination_file_path = _get_destination_file_path(filename, record)
            print('destination_file_path: ', destination_file_path)

            yield {'destination': destination_file_path}

            if os.path.exists(destination_file_path):
                print('File already exists')
                yield {'state': STATE_EXISTS}
                return

            with tempfile.NamedTemporaryFile(delete=False) as temp:
                print('Downloading into tmp file: ', temp.name)
                for upd in downloader.download(record.download_url, temp.name, filename, self._stop_event):
                    yield {'dl': upd}

                shutil.move(temp.name, destination_file_path)
                os.chmod(destination_file_path, 0o644)
                print('Move from tmp file to destination: ', destination_file_path)

            record.md5_hash = _calculate_md5(destination_file_path)
            record.sha256_hash = _calculate_sha256(destination_file_path)

            env.storage.update_record(record)

        except Exception as ex:
            yield {'state': STATE_ERROR, 'exception': ex}
            traceback.print_exc()
            return

        if record.preview_url:
            try:
                preview_filename = _get_preview_filename(record.preview_url, filename)
                print('Preview image name: ', preview_filename)
                yield {'preview_filename': filename}

                preview_destination_file_path = _get_destination_file_path(preview_filename, record)
                print('preview_destination_file_path: ', preview_destination_file_path)
                yield {'preview_destination': destination_file_path}

                preview_downloader = self._get_downloader(record.preview_url)

                with tempfile.NamedTemporaryFile(delete=False) as temp:
                    print('Downloading preview into tmp file: ', temp.name)
                    for upd in preview_downloader.download(record.preview_url, temp.name, preview_filename,
                                                           self._stop_event):
                        yield {'preview_dl': upd}

                    shutil.move(temp.name, preview_destination_file_path)
                    os.chmod(destination_file_path, 0o644)
                    print('Move from tmp file to preview destination: ', preview_destination_file_path)
            except Exception as ex:
                yield {'exception_preview': ex}
                traceback.print_exc()

        yield {'state': STATE_COMPLETED}

    def _get_downloader(self, url: str) -> Downloader:
        for downloader in self._downloaders:
            if downloader.accepts_url(url):
                return downloader
        raise ValueError(f'There is no downloader to handle {self}')
