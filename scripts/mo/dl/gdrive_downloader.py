import threading
from urllib.parse import urlparse

from scripts.mo.dl.downloader import Downloader


class GDriveDownloader(Downloader):
    def accepts_url(self, url: str) -> bool:
        hostname = urlparse(url).hostname
        if hostname == 'drive.google.com' and '/file/' in url:
            try:
                import gdown
                return True
            except ImportError:
                print("gdown package is required to download ", url)
        return False

    def fetch_filename(self, url: str):
        raise NotImplementedError('GDrive not implemented yet')

    def download(self, url: str, destination_file: str, stop_event: threading.Event):
        raise NotImplementedError('GDrive not implemented yet')

# import os
# import re
# from bs4 import BeautifulSoup
# from urllib.parse import urlparse, parse_qs
#
# import gdown
# import requests
#
#
# def _parse_url(url):
#     parsed = urlparse(url)
#     query = parse_qs(parsed.query)
#
#     if parsed.hostname != "drive.google.com":
#         return None
#
#     file_id = None
#     if "id" in query:
#         file_ids = query["id"]
#         if len(file_ids) == 1:
#             file_id = file_ids[0]
#     else:
#         patterns = [
#             r"^/file/d/(.*?)/(edit|view)$",
#             r"^/file/u/[0-9]+/d/(.*?)/(edit|view)$",
#         ]
#         for pattern in patterns:
#             match = re.match(pattern, parsed.path)
#             if match:
#                 file_id = match.groups()[0]
#                 break
#
#     return file_id
#
#
# def fetch_filename(url: str):
#     try:
#         gdrive_file_id = _parse_url(url)
#
#         if gdrive_file_id is None:
#             return None
#
#         url = "https://drive.google.com/uc?id={id}".format(id=gdrive_file_id)
#         sess = requests.session()
#         sess.headers.update(
#             {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6)"}
#         )
#         res = sess.get(url, stream=True, verify=True)
#     except requests.exceptions.ProxyError as e:
#         print(e)
#         return None
#
#     if res.status_code == 200:
#         if 'Content-Disposition' in res.headers:
#             content_disp = res.headers['Content-Disposition']
#             filename_from_url = content_disp.split(';')[1].split('=')[1].strip('\"')
#             return filename_from_url.replace(os.path.sep, "_")
#
#         if res.headers["Content-Type"].startswith("text/html"):
#             soup = BeautifulSoup(res.text, 'html.parser')
#             filename = soup.find('span', {'class': 'uc-name-size'}).find('a').text
#             match = re.search(r'\b\w+\.\w+\b', filename)
#             if match:
#                 return match.group(0)
#     else:
#         return None
#
#
# def accepts_url(url) -> bool:
#     hostname = urlparse(url).hostname
#     return hostname == 'drive.google.com' and '/file/' in url
#
#
# def download(url):
#     g_url = 'https://drive.google.com/file/d/1kTWkSQ-cLs9q1PKfBp4VIDtAbs1NHzNZ/view?usp=share_link'
#     # os.chdir('/Users/alexander/Projects/Python/stable-diffusion-webui/extensions/sd-model-organizer/tmp')
#     gdown.download(url=g_url, quiet=False, fuzzy=True)
#     pass
