# Copyright (c) 2015 - 2018 Kentaro Wada.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# https://github.com/wkentaro/gdown

import threading
from urllib.parse import urlparse, parse_qs
import json
import os
import os.path as osp
import re
import shutil
import sys
import tempfile
import textwrap
import six

import requests
import tqdm
from bs4 import BeautifulSoup

from scripts.mo.dl.downloader import Downloader
from scripts.mo.environment import logger

CHUNK_SIZE = 512 * 1024  # 512KB
home = osp.expanduser("~")


# textwrap.indent for Python2
def _indent(text, prefix):
    def prefixed_lines():
        for line in text.splitlines(True):
            yield prefix + line if line.strip() else line

    return "".join(prefixed_lines())


def _parse_url(url):
    """Parse URLs especially for Google Drive links.

    file_id: ID of file on Google Drive.
    is_download_link: Flag if it is download link of Google Drive.
    """
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    is_gdrive = parsed.hostname in ["drive.google.com"]
    is_download_link = parsed.path.endswith("/uc")

    if not is_gdrive:
        return is_gdrive, is_download_link

    file_id = None
    if "id" in query:
        file_ids = query["id"]
        if len(file_ids) == 1:
            file_id = file_ids[0]
    else:
        patterns = [
            r"^/file/d/(.*?)/(edit|view)$",
            r"^/file/u/[0-9]+/d/(.*?)/(edit|view)$",
        ]
        for pattern in patterns:
            match = re.match(pattern, parsed.path)
            if match:
                file_id = match.groups()[0]
                break

    return file_id, is_download_link


def _get_url_from_gdrive_confirmation(contents):
    url = ""
    for line in contents.splitlines():
        m = re.search(r'href="(\/uc\?export=download[^"]+)', line)
        if m:
            url = "https://docs.google.com" + m.groups()[0]
            url = url.replace("&amp;", "&")
            break
        m = re.search('id="download-form" action="(.+?)"', line)
        if m:
            url = m.groups()[0]
            url = url.replace("&amp;", "&")
            break
        m = re.search('"downloadUrl":"([^"]+)', line)
        if m:
            url = m.groups()[0]
            url = url.replace("\\u003d", "=")
            url = url.replace("\\u0026", "&")
            break
        m = re.search('<p class="uc-error-subcaption">(.*)</p>', line)
        if m:
            error = m.groups()[0]
            raise RuntimeError(error)
    if not url:
        raise RuntimeError(
            "Cannot retrieve the public link of the file. "
            "You may need to change the permission to "
            "'Anyone with the link', or have had many accesses."
        )
    return url


def _get_session(use_cookies, return_cookies_file=False):
    sess = requests.session()

    sess.headers.update(
        {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6)"}
    )

    # Load cookies if exists
    cookies_file = osp.join(home, ".cache/gdown/cookies.json")
    if osp.exists(cookies_file) and use_cookies:
        with open(cookies_file) as f:
            cookies = json.load(f)
        for k, v in cookies:
            sess.cookies[k] = v

    if return_cookies_file:
        return sess, cookies_file
    else:
        return sess


def _download(
        url: str,
        output: str,
        description: str,
        stop_event: threading.Event,
        use_cookies=True,
        verify=True,
        fuzzy=True,
        resume=False,
):
    url_origin = url

    yield {'bytes_ready': 0, 'bytes_total': 0, 'speed_rate': 0, 'elapsed': 0}

    sess, cookies_file = _get_session(use_cookies=use_cookies, return_cookies_file=True)

    if stop_event.is_set():
        return

    gdrive_file_id, is_gdrive_download_link = _parse_url(url)

    if stop_event.is_set():
        return

    if fuzzy and gdrive_file_id:
        # overwrite the url with fuzzy match of a file id
        url = "https://drive.google.com/uc?id={id}".format(id=gdrive_file_id)
        url_origin = url
        is_gdrive_download_link = True

    if stop_event.is_set():
        return

    while True:
        res = sess.get(url, stream=True, verify=verify)

        if stop_event.is_set():
            return

        if url == url_origin and res.status_code == 500:
            # The file could be Google Docs or Spreadsheets.
            url = "https://drive.google.com/open?id={id}".format(
                id=gdrive_file_id
            )
            continue

        if stop_event.is_set():
            return

        if use_cookies:
            if not osp.exists(osp.dirname(cookies_file)):
                os.makedirs(osp.dirname(cookies_file))
            # Save cookies
            with open(cookies_file, "w") as f:
                cookies = [
                    (k, v)
                    for k, v in sess.cookies.items()
                    if not k.startswith("download_warning_")
                ]
                json.dump(cookies, f, indent=2)

        if stop_event.is_set():
            return

        if "Content-Disposition" in res.headers:
            # This is the file
            break
        if not (gdrive_file_id and is_gdrive_download_link):
            break

        # Need to redirect with confirmation
        try:
            url = _get_url_from_gdrive_confirmation(res.text)
        except RuntimeError as e:
            error = "\n".join(textwrap.wrap(str(e)))
            error = _indent(error, "\t")

            raise Exception(f"Access denied with the following error: {error}")

    if stop_event.is_set():
        return

    if gdrive_file_id and is_gdrive_download_link:
        content_disposition = six.moves.urllib_parse.unquote(
            res.headers["Content-Disposition"]
        )
        m = re.search(r"filename\*=UTF-8''(.*)", content_disposition)
        filename_from_url = m.groups()[0]
        filename_from_url = filename_from_url.replace(osp.sep, "_")
    else:
        filename_from_url = osp.basename(url)

    if output is None:
        output = filename_from_url

    if stop_event.is_set():
        return

    output_is_path = isinstance(output, six.string_types)
    if output_is_path and output.endswith(osp.sep):
        if not osp.exists(output):
            os.makedirs(output)
        output = osp.join(output, filename_from_url)

    if output_is_path:
        existing_tmp_files = []
        for file in os.listdir(osp.dirname(output) or "."):
            if file.startswith(osp.basename(output)):
                existing_tmp_files.append(osp.join(osp.dirname(output), file))
        if resume and existing_tmp_files:
            if len(existing_tmp_files) != 1:
                logger.warning("There are multiple temporary files to resume:")
                logger.warning("\n")
                for file in existing_tmp_files:
                    logger.warning(f"\t{file}")
                logger.warning("\n")
                logger.warning("Please remove them except one to resume downloading.")
                return
            tmp_file = existing_tmp_files[0]
        else:
            resume = False
            # mkstemp is preferred, but does not work on Windows
            # https://github.com/wkentaro/gdown/issues/153
            tmp_file = tempfile.mktemp(
                suffix=tempfile.template,
                prefix=osp.basename(output),
                dir=osp.dirname(output),
            )
        f = open(tmp_file, "ab")
    else:
        tmp_file = None
        f = output

    if stop_event.is_set():
        return

    if tmp_file is not None and f.tell() != 0:
        headers = {"Range": "bytes={}-".format(f.tell())}
        res = sess.get(url, headers=headers, stream=True, verify=verify)

    if stop_event.is_set():
        return

    logger.info("Downloading...")
    if resume:
        logger.info(f"Resume: {tmp_file}")
    if url_origin != url:
        logger.info(f"From (uriginal): {url_origin}")
        logger.info(f"From (redirected): {url}")
    else:
        logger.info(f"From: {url}")
    logger.info(f"To: {osp.abspath(output) if output_is_path else output}")

    if stop_event.is_set():
        return

    total = res.headers.get("Content-Length")
    try:
        yield {'bytes_ready': 0, 'bytes_total': total, 'speed_rate': 0, 'elapsed': 0}

        if total is not None:
            total = int(total)

        pbar = tqdm.tqdm(total=total, unit="iB", unit_scale=True, desc=description)

        if stop_event.is_set():
            return

        for chunk in res.iter_content(chunk_size=CHUNK_SIZE):
            f.write(chunk)

            if stop_event.is_set():
                return

            pbar.update(len(chunk))
            format_dict = pbar.format_dict
            yield {
                'bytes_ready': format_dict['n'],
                'bytes_total': format_dict['total'],
                'speed_rate': format_dict['rate'],
                'elapsed': format_dict['elapsed']
            }

        pbar.close()

        if tmp_file:
            f.close()
            shutil.move(tmp_file, output)

        yield {
            'bytes_ready': total,
            'bytes_total': total,
            'speed_rate': 0,
            'elapsed': 0
        }
    finally:
        sess.close()

    return output


class GDriveDownloader(Downloader):
    def accepts_url(self, url: str) -> bool:
        hostname = urlparse(url).hostname
        return hostname == 'drive.google.com' and '/file/' in url

    def fetch_filename(self, url: str):
        try:
            gdrive_file_id, is_gdrive_download_link = _parse_url(url)

            if gdrive_file_id is None:
                return None

            url = "https://drive.google.com/uc?id={id}".format(id=gdrive_file_id)
            sess = _get_session(use_cookies=True, return_cookies_file=False)
            res = sess.get(url, stream=True, verify=True)
        except Exception as e:
            logger.warning(e)
            return None

        if res.status_code == 200:
            if 'Content-Disposition' in res.headers:
                content_disp = res.headers['Content-Disposition']
                filename_from_url = content_disp.split(';')[1].split('=')[1].strip('\"')
                return filename_from_url.replace(os.path.sep, "_")

            if res.headers["Content-Type"].startswith("text/html"):
                soup = BeautifulSoup(res.text, 'html.parser')
                filename = soup.find('span', {'class': 'uc-name-size'}).find('a').text
                match = re.search(r'\b\w+\.\w+\b', filename)
                if match:
                    return match.group(0)
        else:
            return None

    def download(self, url: str, destination_file: str, description: str, stop_event: threading.Event):
        yield from _download(url=url,
                             output=destination_file,
                             description=description,
                             stop_event=stop_event)
