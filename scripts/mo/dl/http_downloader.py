import threading
from urllib.parse import urlparse

import requests
from requests.exceptions import ConnectTimeout, HTTPError, ConnectionError
from tqdm import tqdm

from scripts.mo.dl.downloader import Downloader
from scripts.mo.environment import env

def _civitai_api_url(url: str, api_key: str = None) -> str:
    parsed_url = urlparse(url)
    if api_key and parsed_url.hostname == 'civitai.com':
        url = url + '&token=' + api_key if "?" in url else url + '?token=' + api_key
    return url

class HttpDownloader(Downloader):

    def accepts_url(self, url: str) -> bool:
        parsed_url = urlparse(url)
        return parsed_url.scheme in ['http', 'https'] and parsed_url.hostname not in ['drive.google.com', 'mega.nz']

    def check_url_available(self, url: str):
        url = _civitai_api_url(url, env.api_key())
        try:
            response = requests.get(url, stream=True, timeout=10)
            response.raise_for_status()
            response.close()
            return True, None
        except ConnectTimeout as ex:
            return False, ex
        except ConnectionError as ex:
            return False, ex
        except HTTPError as ex:
            if ex.response.status_code == 401:
                error_message = 'Invalid API key, please check API key in Settings > Model Organizer > Civitai API Key.'
                return False, error_message
            return False, ex
        except Exception as ex:
            return False, ex

    def fetch_filename(self, url):

        api_key = env.api_key()
        headers = {'Range': 'bytes=0-1'}
        if api_key:
            headers['Authorization'] = 'Bearer ' + api_key

        response = requests.get(url, headers=headers)
        if response.status_code == 200 or response.status_code == 206:
            if 'Content-Disposition' in response.headers:
                content_disp = response.headers['Content-Disposition']
                filename = content_disp.split(';')[1].split('=')[1].strip('\"')
                return (filename.encode('utf-8').decode('GBK').encode('utf-8')
                        .decode('utf-8'))  # Needed to properly encode/decode chinese symbols, have fun.
        else:
            return None

    def download(self, url: str, destination_file: str, description: str, stop_event: threading.Event):
        if stop_event.is_set():
            return

        yield {'bytes_ready': 'None', 'bytes_total': 'None', 'speed_rate': 'None', 'elapsed': 'None'}

        api_key = env.api_key()
        if api_key:
            auth_header = {'Content-Type': 'application/json',
                           'Authorization': 'Bearer ' + api_key}
            response = requests.get(url, stream=True, headers=auth_header)
        else:
            response = requests.get(url, stream=True)

        total_size = int(response.headers.get('content-length', 0))

        yield {'bytes_ready': 0, 'bytes_total': total_size, 'speed_rate': 0, 'elapsed': 0}

        if stop_event.is_set():
            return

        progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True, desc=description)

        with open(destination_file, 'wb') as file:

            if stop_event.is_set():
                progress_bar.close()
                return

            for data in response.iter_content(1024):

                if stop_event.is_set():
                    progress_bar.close()
                    return

                file.write(data)
                progress_bar.update(len(data))
                format_dict = progress_bar.format_dict

                yield {
                    'bytes_ready': format_dict['n'],
                    'bytes_total': format_dict['total'],
                    'speed_rate': format_dict['rate'],
                    'elapsed': format_dict['elapsed']
                }
        yield {
            'bytes_ready': format_dict['n'],
            'bytes_total': format_dict['n'],
            'speed_rate': format_dict['rate'],
            'elapsed': format_dict['elapsed']
        }
        progress_bar.close()
