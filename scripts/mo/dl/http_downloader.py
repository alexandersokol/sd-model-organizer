import threading
from urllib.parse import urlparse

import requests
import requests_cache
from tqdm import tqdm

from scripts.mo.dl.downloader import Downloader
from scripts.mo.environment import env


class HttpDownloader(Downloader):

    def accepts_url(self, url: str) -> bool:
        parsed_url = urlparse(url)
        return parsed_url.scheme in ['http', 'https'] and parsed_url.hostname not in ['drive.google.com', 'mega.nz']

    def fetch_filename(self, url):
        headers = {'Accept-Encoding': 'identity'}
        api_key = env.api_key()
        if api_key:
            headers['Authorization'] = 'Bearer ' + api_key

        # Read only the headers. A Range probe can leave a cached partial response
        # at the same URL that is subsequently used for the actual download.
        with requests_cache.disabled():
            with requests.get(url, headers=headers, stream=True, timeout=30) as response:
                response.raise_for_status()
                if 'Content-Disposition' in response.headers:
                    content_disp = response.headers['Content-Disposition']
                    filename = content_disp.split(';')[1].split('=')[1].strip('"')
                    return (filename.encode('utf-8').decode('GBK').encode('utf-8')
                            .decode('utf-8'))
        return None

    def download(self, url: str, destination_file: str, description: str, stop_event: threading.Event):
        if stop_event.is_set():
            return

        yield {'bytes_ready': 'None', 'bytes_total': 'None', 'speed_rate': 'None', 'elapsed': 'None'}

        headers = {'Accept-Encoding': 'identity'}
        api_key = env.api_key()
        if api_key:
            headers['Authorization'] = 'Bearer ' + api_key

        with requests_cache.disabled():
            with requests.get(url, stream=True, headers=headers, timeout=30) as response:
                try:
                    response.raise_for_status()
                except requests.HTTPError as error:
                    if response.status_code in (401, 403):
                        raise requests.HTTPError(
                            'Download authorization failed. For Civitai, configure a valid API key '
                            'in Model Organizer settings and ensure your account has access to this model.',
                            response=response) from error
                    raise
                if response.status_code != 200 or 'Content-Range' in response.headers:
                    raise ValueError('Server returned a partial or unexpected response; model was not saved.')
                content_type = response.headers.get('Content-Type', '').split(';')[0].strip().lower()
                if content_type in ('text/html', 'application/xhtml+xml', 'application/json'):
                    raise ValueError('Server returned an error page instead of a downloadable file.')

                total_size = int(response.headers.get('Content-Length', 0))
                yield {'bytes_ready': 0, 'bytes_total': total_size, 'speed_rate': 0, 'elapsed': 0}
                if stop_event.is_set():
                    return

                with tqdm(total=total_size, unit='iB', unit_scale=True, desc=description) as progress_bar:
                    with open(destination_file, 'wb') as file:
                        for data in response.iter_content(1024):
                            if stop_event.is_set():
                                return
                            file.write(data)
                            progress_bar.update(len(data))
                            stats = progress_bar.format_dict
                            yield {'bytes_ready': stats['n'], 'bytes_total': total_size,
                                   'speed_rate': stats['rate'], 'elapsed': stats['elapsed']}

                    stats = progress_bar.format_dict
                    if stats['n'] == 0:
                        raise ValueError('Server returned an empty file.')
                    # Content-Length describes encoded bytes if the server ignores identity.
                    if total_size and not response.headers.get('Content-Encoding') and stats['n'] != total_size:
                        raise ValueError('Download is incomplete: received bytes do not match Content-Length.')
                    yield {'bytes_ready': stats['n'], 'bytes_total': stats['n'],
                           'speed_rate': stats['rate'], 'elapsed': stats['elapsed']}
