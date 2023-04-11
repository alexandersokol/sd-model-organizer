import random
import string
from loremipsum import generate_paragraphs, generate_sentence
from scripts.mo.sqlite_storage import SQLiteStorage


from scripts.mo.models import Record, ModelType

def generate_random_url():
    protocol = random.choice(['http', 'https'])
    domain = ''.join(random.choice(string.ascii_lowercase) for _ in range(random.randint(2, 10))) + '.com'
    path = '/'.join(''.join(random.choice(string.ascii_lowercase) for _ in range(random.randint(2, 10))) for _ in range(random.randint(1, 5)))
    query_params = ''.join(random.choice(string.ascii_lowercase) for _ in range(random.randint(5, 10))) + '=' + ''.join(random.choice(string.ascii_lowercase) for _ in range(random.randint(5, 10)))
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
storage = SQLiteStorage()

# for record in records:
#     storage.add_record(record)
#     print(record)

print(f'Done. ')

