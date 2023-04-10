from enum import Enum


class ModelType(Enum):
    STABLE_DIFFUSION = 'Stable Diffusion'
    VAE = 'VAE'
    LORA = 'Lora'
    HYPER_NETWORK = 'Hyper Network'
    EMBEDDING = 'Embedding'
    OTHER = 'Other'

    @staticmethod
    def by_value(value: str):
        for model_type in ModelType:
            if model_type.value == value.strip():
                return model_type
        raise ValueError(f'There is no model type defined with name "{value}"')


class Record:
    def __init__(self, id_,
                 name: str,
                 model_type: ModelType,
                 download_url: str,
                 url: str = '',
                 download_path: str = '',
                 download_filename: str = '',
                 preview_url: str = '',
                 description: str = '',
                 positive_prompts: str = '',
                 negative_prompts: str = '',
                 model_hash: str = '',
                 md5_hash: str = ''):
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
        self.model_hash = model_hash
        self.md5_hash = md5_hash

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
               f'model_hash="{self.model_hash}", ' \
               f'md5_hash="{self.md5_hash}"'
