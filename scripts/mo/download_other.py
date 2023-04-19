import os

import requests
from tqdm import tqdm


def fetch_filename(url):
    response = requests.get(url, headers={'Range': 'bytes=0-1'})
    if response.status_code == 200 or response.status_code == 206:
        if 'Content-Disposition' in response.headers:
            content_disp = response.headers['Content-Disposition']
            return content_disp.split(';')[1].split('=')[1].strip('\"')
    else:
        return None


def download_from_url(url: str, destination_file: str, temp_dir: str):
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))

    progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True, desc=destination_file)

    yield {
        'bytes_ready': 0,
        'bytes_total': total_size,
        'speed_rate': 0,
        'elapsed': 0
    }

    with open(os.path.join(temp_dir, destination_file), 'wb') as file:
        for data in response.iter_content(1024):
            file.write(data)
            progress_bar.update(len(data))
            print(progress_bar.format_meter(**progress_bar.format_dict))
            format_dict = progress_bar.format_dict
            yield {
                'bytes_ready': format_dict['n'],
                'bytes_total': format_dict['total'],
                'speed_rate': format_dict['rate'],
                'elapsed': format_dict['elapsed']
            }

        progress_bar.close()
