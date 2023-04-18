from urllib.parse import urlparse

from mega import Mega

_mega_instance = None


def _mega() -> Mega:
    global _mega_instance
    if _mega_instance is None:
        _mega_instance = Mega()
        _mega_instance.login()
    return _mega_instance


def accepts_url(url) -> bool:
    hostname = urlparse(url).hostname
    return hostname == 'mega.nz'


def fetch_filename(url: str):
    try:
        return _mega().get_public_url_info(url)['name']
    except Exception as ex:
        print(ex)
        return None

def download(url: str):
    mega = Mega()
    m = mega.login()
    m_url = ''
    m.download_url(m_url,
                   dest_path='/Users/alexander/Projects/Python/stable-diffusion-webui/extensions/sd-model-organizer/tmp')
