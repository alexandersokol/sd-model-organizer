import os
import re
import threading
import traceback

import requests
from urllib.parse import urlparse

import scripts.mo.download_gdown as gdwn
import scripts.mo.download_mega as mdwn
import scripts.mo.download_other as odwn

from scripts.mo.environment import env


class DownloadState:
    __instance = None
    __lock = threading.Lock()

    def __init__(self):
        self.is_download_cancelled = False

    @staticmethod
    def get_instance():
        if DownloadState.__instance is None:
            with DownloadState.__lock:
                if DownloadState.__instance is None:
                    DownloadState.__instance = DownloadState()
        return DownloadState.__instance


def _verify_filename(filename):
    pattern = r'^[a-zA-Z0-9_-]+\.[a-zA-Z0-9]{1,12}$'
    _, ext = os.path.splitext(filename)
    if re.match(pattern, filename):
        return True
    else:
        return False


def temp_dir():
    return os.path.join(env.mo_script_dir, 'tmp')


def fetch_filename(url: str):
    try:
        url_filename = os.path.basename(urlparse(url).path)
        if _verify_filename(url_filename):
            return url_filename

        if gdwn.accepts_url(url):
            return gdwn.fetch_filename(url)
        elif mdwn.accepts_url(url):
            return mdwn.fetch_filename(url)
        else:
            return odwn.fetch_filename(url)

    except Exception as ex:
        print(type(ex).__name__, str(ex))
        return None


def download_from_url(url: str, destination_file: str):
    yield from odwn.download_from_url(url, destination_file, temp_dir())


def clean_up_temp_dir():
    tmp_dir_path = temp_dir()
    for filename in os.listdir(tmp_dir_path):
        file_path = os.path.join(tmp_dir_path, filename)
        if os.path.isdir(file_path):
            import shutil
            shutil.rmtree(file_path)
        else:
            os.remove(file_path)