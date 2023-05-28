import os.path
from enum import Enum


class ModelType(Enum):
    CHECKPOINT = 'Checkpoint'
    VAE = 'VAE'
    LORA = 'Lora'
    HYPER_NETWORK = 'Hyper Network'
    LYCORIS = 'LyCORIS'
    EMBEDDING = 'Embedding'
    OTHER = 'Other'

    @staticmethod
    def by_value(value: str):
        for model_type in ModelType:
            if model_type.value == value.strip():
                return model_type
        raise ValueError(f'There is no model type defined with name "{value}"')


class ModelSort(Enum):
    TIME_ADDED_ASC = 'Time Added'
    TIME_ADDED_DESC = 'Time Added Reversed'
    NAME_ASC = 'Name'
    NAME_DESC = 'Name Reversed'

    @staticmethod
    def by_value(value: str):
        for model_sort in ModelSort:
            if model_sort.value == value.strip():
                return model_sort
        raise ValueError(f'There is no model sort defined with name "{value}"')


class Record:
    def __init__(self, id_,
                 name: str,
                 model_type: ModelType,
                 download_url: str = '',
                 url: str = '',
                 download_path: str = '',
                 download_filename: str = '',
                 preview_url: str = '',
                 description: str = '',
                 positive_prompts: str = '',
                 negative_prompts: str = '',
                 sha256_hash: str = '',
                 md5_hash: str = '',
                 location: str = '',
                 created_at: float = 0,
                 groups=None,
                 subdir: str = ''):
        if groups is None:
            groups = []

        self.id_ = id_
        self.name = name
        self.model_type = model_type
        self.url = url
        self.download_url = download_url
        self.download_path = download_path
        self.download_filename = download_filename
        self.preview_url = preview_url
        self.description = description
        self.positive_prompts = positive_prompts
        self.negative_prompts = negative_prompts
        self.sha256_hash = sha256_hash
        self.md5_hash = md5_hash
        self.location = location
        self.created_at = created_at
        self.groups = groups
        self.subdir = subdir

    def is_file_exists(self) -> bool:
        return bool(self.location) and os.path.isfile(self.location)

    def is_downloadable(self) -> bool:
        return bool(self.download_url)

    def is_download_possible(self) -> bool:
        return self.is_downloadable() and not self.is_file_exists()

    def __str__(self):
        return f'id="{self.id_}", ' \
               f'name="{self.name}", ' \
               f'model_type="{self.model_type}", ' \
               f'url="{self.url}", ' \
               f'download_url="{self.download_url}", ' \
               f'download_path="{self.download_path}", ' \
               f'download_filename="{self.download_filename}", ' \
               f'preview_url="{self.preview_url}", ' \
               f'description="{self.description}", ' \
               f'positive_prompts="{self.positive_prompts}", ' \
               f'negative_prompts="{self.negative_prompts}", ' \
               f'sha256_hash="{self.sha256_hash}", ' \
               f'md5_hash="{self.md5_hash}", ' \
               f'location="{self.location}", ' \
               f'created_at="{self.created_at}", ' \
               f'groups="{self.groups}", ' \
               f'subdir="{self.subdir}".'
