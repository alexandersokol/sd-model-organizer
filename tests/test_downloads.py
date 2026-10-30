import hashlib
import io
import logging
import tempfile
import threading
import unittest
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import patch

import requests

from scripts.mo.dl.http_downloader import HttpDownloader
from scripts.mo.environment import env


def response(status=200, body=b'model bytes', **headers):
    result = requests.Response()
    result.status_code = status
    result.url = 'https://civitai.com/api/download/models/1707179?fileId=1607800'
    result.headers.update(headers)
    result.raw = io.BytesIO(body)
    return result


class HttpDownloadTests(unittest.TestCase):
    def setUp(self):
        self.api_key = patch.object(env, 'api_key', return_value='', create=True)
        self.api_key.start()
        self.addCleanup(self.api_key.stop)
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'model'

    def download(self, reply):
        with patch('requests.get', return_value=reply):
            return list(HttpDownloader().download(reply.url, str(self.path), 'test', threading.Event()))

    def test_authentication_error_is_not_saved_as_model(self):
        with self.assertRaises(requests.HTTPError):
            self.download(response(401, b'{"error":"Unauthorized"}', **{'Content-Type': 'application/json'}))
        self.assertFalse(self.path.exists())

    def test_unsolicited_partial_response_is_rejected(self):
        with self.assertRaises(ValueError):
            self.download(response(206, b'mo', **{'Content-Range': 'bytes 0-1/100'}))
        self.assertFalse(self.path.exists())

    def test_html_error_page_with_success_status_is_rejected(self):
        with self.assertRaises(ValueError):
            self.download(response(body=b'<html>Login</html>', **{'Content-Type': 'text/html'}))

    def test_short_body_is_rejected(self):
        with self.assertRaises(ValueError):
            self.download(response(body=b'mo', **{'Content-Length': '100'}))

    def test_full_download_without_content_length(self):
        updates = self.download(response())
        self.assertEqual(self.path.read_bytes(), b'model bytes')
        self.assertEqual(updates[-1]['bytes_ready'], 11)

    def test_empty_download_is_rejected(self):
        with self.assertRaises(ValueError):
            self.download(response(body=b''))

    def test_filename_probe_does_not_request_partial_content(self):
        def get(url, **kwargs):
            self.assertNotIn('Range', kwargs.get('headers', {}))
            self.assertTrue(kwargs.get('stream'))
            return response(**{'Content-Disposition': 'attachment; filename="model.safetensors"'})
        with patch('requests.get', side_effect=get):
            self.assertEqual(HttpDownloader().fetch_filename('https://example.com/model'), 'model.safetensors')


class IntegrityTests(unittest.TestCase):
    def test_wrong_model_is_not_published_or_saved(self):
        self.check_integrity(hashlib.sha256(b'correct model').hexdigest(), False)

    def test_matching_model_is_published(self):
        self.check_integrity(hashlib.sha256(b'wrong model').hexdigest().upper(), True)

    def test_model_without_expected_hash_is_published(self):
        self.check_integrity('', True)

    def check_integrity(self, expected_hash, valid):
        # The WebUI-only image helpers cannot be imported outside the host app.
        utils = ModuleType('scripts.mo.utils')
        utils.resize_preview_image = lambda *args: None
        utils.get_model_filename_without_extension = lambda name: name
        utils.calculate_sha256 = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()
        with patch.dict('sys.modules', {'scripts.mo.utils': utils}):
            from scripts.mo.dl.download_manager import DownloadManager
        with tempfile.TemporaryDirectory() as directory:
            record = SimpleNamespace(id_=1, download_url='https://example.com/model',
                                     download_filename='model.safetensors', download_path=directory,
                                     subdir='', sha256_hash=expected_hash,
                                     location='', md5_hash='', preview_url='')
            class WrongDownloader:
                def download(self, url, path, description, stop):
                    Path(path).write_bytes(b'wrong model')
                    yield {}
            manager = DownloadManager()
            manager._stop_event.clear()
            saved = []
            storage = SimpleNamespace(update_record=saved.append)
            with patch.object(manager, '_get_downloader', return_value=WrongDownloader()), \
                 patch.object(env, 'storage', storage, create=True), \
                 patch.object(logging.getLogger('scripts.mo.environment'), 'exception'):
                updates = list(manager._download_record(record))
            destination = Path(directory) / 'model.safetensors'
            self.assertEqual(updates[-1]['status'], 'Completed' if valid else 'Error')
            self.assertEqual(destination.exists(), valid)
            self.assertEqual(saved, [record] if valid else [])
            if valid:
                self.assertEqual(destination.read_bytes(), b'wrong model')
                self.assertEqual(record.sha256_hash, hashlib.sha256(b'wrong model').hexdigest())
            else:
                self.assertEqual(record.location, '')
                self.assertEqual(record.sha256_hash, expected_hash)
                self.assertEqual(list(Path(directory).iterdir()), [])
            manager._clear_temp_files()


if __name__ == '__main__':
    unittest.main()
