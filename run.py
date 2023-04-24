import random
import string

from loremipsum import generate_paragraphs, generate_sentence

from scripts.mo.environment import env, logger
from scripts.mo.init_storage import initialize_storage
from scripts.mo.models import Record, ModelType


def read_settings():
    with open('settings.txt') as f:
        lines = f.readlines()

    result = {}
    for line in lines:
        key, value = line.strip().split(': ')
        result[key] = value
        logger.info(f'{key}: {value}')
    logger.info('Settings loaded.')
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


# initialize_storage()
#
# storage = SQLiteStorage()
# records = storage.get_records_by_group('first')


urls = [
    'https://drive.google.com/file/d/1kTWkSQ-cLs9q1PKfBp4VIDtAbs1NHzNZ/view?usp=share_link',
    'https://drive.google.com/uc?id=1kTWkSQ-cLs9q1PKfBp4VIDtAbs1NHzNZ',
    'https://drive.google.com/file/d/1-cSYdG-b2MGNJrARjSZEDDf0J_3dKvzZ/view?usp=sharing',
    'https://civitai.com/api/download/models/7425',
    'https://civitai.com/api/download/models/5057',
    'https://huggingface.co/Linaqruf/anything-v3.0/resolve/main/anything-v3-fp32-pruned.safetensors',
    'https://huggingface.co/stabilityai/stable-diffusion-2-1/resolve/main/v2-1_768-ema-pruned.ckpt',
    'https://drive.google.com/file/d/1-cSYdG-b2MGNJrARjSZEDDf0J_3dKvzZ/view?usp=share_link',
    'https://drive.google.com/file/d/1-cSYdG-b2MGNJrARjSZEDDf0J_3dKvzZ/view?usp=share_link',
    'https://mega.nz/file/sg9hwJKA#Xs0oDDS81Qlo0OdVxc8aAiweZq5ANrD5YG-9CKn-QyI',
    'https://mega.nz/file/9x1ERB4R#6t-yFBqqNsNB2H91naOi4H1xsqP7yT7dYt7INq1-12I',
    'ftp://mega.nz/file/9x1ERB4R#6t-yFBqqNsNB2H91naOi4H1xsqP7yT7dYt7INq1-12I'
]

logger.info(f'Done. ')
