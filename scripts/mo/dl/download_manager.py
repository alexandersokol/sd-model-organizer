import os
import shutil
import tempfile
import threading
from copy import deepcopy
from urllib.parse import urlparse

from scripts.mo.dl.downloader import Downloader
from scripts.mo.dl.gdrive_downloader import GDriveDownloader
from scripts.mo.dl.http_downloader import HttpDownloader
from scripts.mo.dl.mega_downloader import MegaDownloader
from scripts.mo.environment import env, logger, calculate_md5, calculate_sha256
from scripts.mo.models import Record

GENERAL_STATUS_IN_PROGRESS = 'In Progress'
GENERAL_STATUS_CANCELLED = 'Cancelled'
GENERAL_STATUS_ERROR = 'Error'
GENERAL_STATUS_COMPLETED = 'Completed'

RECORD_STATUS_PENDING = 'Pending'
RECORD_STATUS_IN_PROGRESS = 'In Progress'
RECORD_STATUS_COMPLETED = 'Completed'
RECORD_STATUS_EXISTS = 'Exists'
RECORD_STATUS_ERROR = 'Error'
RECORD_STATUS_CANCELLED = 'Cancelled'


def _get_destination_file_path(filename: str, record: Record) -> str:
    path = record.download_path
    if not path:
        path = env.get_model_path(record.model_type)
        if path is None:
            raise Exception(f'Destination path is undefined.')

    path = os.path.join(path, record.subdir)
    if not os.path.isdir(path):
        os.makedirs(path)

    return os.path.join(path, filename)


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
            logger.warning('Download already running')
            return

        self._stop_event.clear()
        self._state = {}
        self._latest_state = {}
        self._state_update(general_status=GENERAL_STATUS_IN_PROGRESS)
        self._thread = threading.Thread(target=self._download_loop, args=(records,), daemon=True)
        self._thread.start()

    def stop_download(self):
        if self._stop_event.is_set():
            logger.warning('Download not running')
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

        if general_status == GENERAL_STATUS_CANCELLED and new_general_state.get('records') is not None:
            for key, value in new_general_state['records'].items():
                if value.get('status') and \
                        (value['status'] == RECORD_STATUS_PENDING or value['status'] == RECORD_STATUS_IN_PROGRESS):
                    value['status'] = RECORD_STATUS_CANCELLED

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

            exception = None
            for key, value in self._state['records'].items():
                if value.get('exception') is not None:
                    exception = value['exception']
                    break

            if exception is not None:
                self._state_update(general_status=GENERAL_STATUS_ERROR)
            else:
                self._state_update(general_status=GENERAL_STATUS_COMPLETED)

        except Exception as ex:
            self._state_update(general_status=GENERAL_STATUS_ERROR, exception=str(ex))
            logger.exception(ex)

        self._stop_event.set()
        self._running = False

    def _download_record(self, record: Record):
        try:
            yield {'status': RECORD_STATUS_IN_PROGRESS}

            downloader = self._get_downloader(record.download_url)
            logger.debug('Start download record with id: %s', record.id_)

            if self._stop_event.is_set():
                return

            filename = _get_filename(downloader, record)
            logger.debug('filename: %s', filename)

            yield {'filename': filename}

            if self._stop_event.is_set():
                return

            destination_file_path = _get_destination_file_path(filename, record)
            logger.debug('destination_file_path: %s', destination_file_path)

            yield {'destination': destination_file_path}

            if os.path.exists(destination_file_path):
                logger.debug('File already exists')
                yield {'status': RECORD_STATUS_EXISTS}
                return

            if self._stop_event.is_set():
                return

            with tempfile.NamedTemporaryFile(delete=False) as temp:
                logger.debug('Downloading into tmp file: %s', temp.name)
                for upd in downloader.download(record.download_url, temp.name, filename, self._stop_event):
                    yield {'dl': upd}

                if self._stop_event.is_set():
                    return
                shutil.move(temp.name, destination_file_path)
                os.chmod(destination_file_path, 0o644)
                logger.debug('Move from tmp file to destination: %s', destination_file_path)

            record.location = destination_file_path
            record.md5_hash = calculate_md5(destination_file_path)
            record.sha256_hash = calculate_sha256(destination_file_path)

            env.storage.update_record(record)

        except Exception as ex:
            yield {'status': RECORD_STATUS_ERROR, 'exception': ex}
            logger.exception(ex)
            return

        if self._stop_event.is_set():
            return

        if record.preview_url and env.mo_download_preview():
            try:
                preview_filename = _get_preview_filename(record.preview_url, filename)
                logger.debug('Preview image name: %s', preview_filename)
                yield {'preview_filename': preview_filename}

                if self._stop_event.is_set():
                    return

                preview_destination_file_path = _get_destination_file_path(preview_filename, record)
                logger.debug('preview_destination_file_path: %s', preview_destination_file_path)
                yield {'preview_destination': preview_destination_file_path}

                if self._stop_event.is_set():
                    return

                preview_downloader = self._get_downloader(record.preview_url)

                with tempfile.NamedTemporaryFile(delete=False) as temp:
                    logger.debug('Downloading preview into tmp file: %s', temp.name)
                    for upd in preview_downloader.download(record.preview_url, temp.name, preview_filename,
                                                           self._stop_event):
                        yield {'preview_dl': upd}

                    if self._stop_event.is_set():
                        return

                    shutil.move(temp.name, preview_destination_file_path)
                    os.chmod(destination_file_path, 0o644)
                    logger.debug('Move from tmp file to preview destination: %s', preview_destination_file_path)
            except Exception as ex:
                yield {'exception_preview': ex}
                logger.exception(ex)

        yield {'status': RECORD_STATUS_COMPLETED}

    def _get_downloader(self, url: str) -> Downloader:
        for downloader in self._downloaders:
            if downloader.accepts_url(url):
                return downloader
        raise ValueError(f'There is no downloader to handle {self}')

    def check_url_can_be_handled(self, url: str) -> bool:
        for downloader in self._downloaders:
            if downloader.accepts_url(url):
                return True
        return False
