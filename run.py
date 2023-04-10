from scripts.mo.sqlite_repository import SQLiteRepository
from scripts.mo.models import Record, ModelType

repo = SQLiteRepository()
record = Record(
    id_=None,
    name='Awesome model',
    model_type=ModelType.STABLE_DIFFUSION,
    download_url='https://download.url',
    url='https://model.url',
    download_path='/download/path',
    download_filename='model.safetensors',
    preview_url='https://priview.url',
    description='My awesome model description',
    positive_prompts='good, nice, wonderful, prompt',
    negative_prompts='bad, ugly, obsolete, prompt',
    model_hash='a1b2c3',
    md5_hash='sdkasjkdj109d51k2d'
)
print('Adding new record:')
repo.add_record(record)

print('Fetching all records:')
results = repo.fetch_data()
for result in results:
    print(result)

print(f'Fetch by id {results[0].id_}:')
print(repo.fetch_data_by_id(results[0].id_))

print(f'Remove by id {results[0].id_}')
repo.remove_record(results[0].id_)

print('Done.')
