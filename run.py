import os
import random

import gdown
import requests
import string
from urllib.parse import urlparse
from mega import Mega

from loremipsum import generate_paragraphs, generate_sentence

from scripts.mo.environment import env
from scripts.mo.init_storage import initialize_storage
from scripts.mo.models import Record, ModelType
from scripts.mo.sqlite_storage import SQLiteStorage


SETTINGS_FILE = 'settings.txt'


def read_settings():
    with open(SETTINGS_FILE) as f:
        lines = f.readlines()

    result = {}
    for line in lines:
        key, value = line.strip().split(': ')
        result[key] = value
        print(f'{key}: {value}')
    print('Settings loaded.')
    return result


settings = read_settings()

env.mo_storage_type = lambda: settings['mo_storage_type']
env.mo_notion_api_token = lambda: settings['mo_notion_api_token']
env.mo_notion_db_id = lambda: settings['mo_notion_db_id']
env.mo_model_path = lambda: settings['mo_model_path']
env.mo_vae_path = lambda: settings['mo_vae_path']
env.mo_lora_path = lambda: settings['mo_lora_path']
env.mo_hypernetworks_path = lambda: settings['mo_hypernetworks_path']
env.mo_embeddings_path = lambda: settings['mo_embeddings_path']
env.mo_script_dir = ''
env.mo_layout = lambda: settings['mo_layout']
env.mo_card_width = lambda: settings['mo_card_width']
env.mo_card_height = lambda: settings['mo_card_height']
initialize_storage()

def generate_random_url():
    protocol = random.choice(['http', 'https'])
    domain = ''.join(random.choice(string.ascii_lowercase) for _ in range(random.randint(2, 10))) + '.com'
    path = '/'.join(''.join(random.choice(string.ascii_lowercase) for _ in range(random.randint(2, 10))) for _ in
                    range(random.randint(1, 5)))
    query_params = ''.join(random.choice(string.ascii_lowercase) for _ in range(random.randint(5, 10))) + '=' + ''.join(
        random.choice(string.ascii_lowercase) for _ in range(random.randint(5, 10)))
    return f"{protocol}://{domain}/{path}?{query_params}"


def generate_random_records(count: int):
    results = []
    model_types = [model_type for model_type in ModelType]
    for i in range(0, count):
        pic_id = random.randint(1, 1000)
        pic_width = random.randrange(100, 501, 20)
        pic_height = random.randrange(100, 501, 20)

        description = ''
        for paragraph in generate_paragraphs(1):
            description += paragraph[2]

        r = Record(
            id_=None,
            name=generate_sentence()[2].replace("'", ""),
            model_type=model_types[random.randrange(0, 6)],
            download_url=generate_random_url(),
            url=generate_random_url(),
            preview_url=f'https://picsum.photos/id/{pic_id}/{pic_width}/{pic_height}',
            description=description.replace("'", ""),
        )
        results.append(r)
    return results


# records = generate_random_records(10)
# storage = SQLiteStorage()

# for record in records:
#     storage.add_record(record)
#     print(record)

url = 'https://civitai.com/api/download/models/11745'
response = requests.get(url, headers={'Range': 'bytes=0-1'})

# if response.status_code == 200 or response.status_code == 206:
#     # Extract filename from Content-Disposition header
#     if 'Content-Disposition' in response.headers:
#         content_disp = response.headers['Content-Disposition']
#         filename = content_disp.split(';')[1].split('=')[1].strip('\"')
#     else:
#         # If Content-Disposition header not present, extract filename from URL
#         filename = os.path.basename(urlparse(url).path)
#     print(f"Filename: {filename}")
# else:
#     print("Error: could not download file.")

# g_url = 'https://drive.google.com/file/d/1kTWkSQ-cLs9q1PKfBp4VIDtAbs1NHzNZ/view?usp=share_link'
# os.chdir('/Users/alexander/Projects/Python/stable-diffusion-webui/extensions/sd-model-organizer/tmp')
# gdown.download(url=g_url, quiet=False, fuzzy=True)

# m_url = 'https://mega.nz/file/Z5cy1L7J#YK9tSVGdfipONiHNjJU8ju1e3ahnUsouFIVFKLRWVg4'
# mega = Mega()
# m = mega.login()
# m.download_url(m_url, dest_path='/Users/alexander/Projects/Python/stable-diffusion-webui/extensions/sd-model-organizer/tmp')


initialize_storage()

storage = SQLiteStorage()
records = storage.fetch_data()

print(storage.get_available_groups())
print(f'Done. ')
