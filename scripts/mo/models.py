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
    def __init__(self, _id,
                 name: str, model_type: ModelType, download_url: str,
                 url: str = '',
                 download_path: str = '',
                 download_filename: str = '',
                 preview_url: str = '',
                 description: str = '',
                 positive_prompts: str = '',
                 negative_prompts: str = ''):
        self.id_ = _id
        self.name = name
        self.model_type = model_type
        self.url = url
        self.download_url = download_url
        self.download_path = download_path
        self.download_filename = download_filename,
        self.preview_url = preview_url
        self.description = description
        self.positive_prompts = positive_prompts
        self.negative_prompts = negative_prompts

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
               f'negative_prompts="{self.negative_prompts}"'
