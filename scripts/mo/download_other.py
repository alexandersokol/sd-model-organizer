import requests


def fetch_filename(url):
    response = requests.get(url, headers={'Range': 'bytes=0-1'})
    if response.status_code == 200 or response.status_code == 206:
        if 'Content-Disposition' in response.headers:
            content_disp = response.headers['Content-Disposition']
            return content_disp.split(';')[1].split('=')[1].strip('\"')
    else:
        return None
