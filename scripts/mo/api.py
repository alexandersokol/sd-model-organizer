import time

from fastapi import FastAPI

from scripts.mo.data.storage import map_record_to_dict
from scripts.mo.environment import logger, env


def init_extension_api(app: FastAPI):
    @app.get(f"/gg/hello")
    async def greeting():
        logger.debug('Greetings api called')
        return {
            'message': 'Hello',
            'date': time.time()
        }

    @app.get(f"/gg/models")
    async def get_models():
        records = env.storage.get_all_records()
        records_dict = list(map(lambda r: map_record_to_dict(r), records))
        return records_dict

    @app.get(f"/gg/model")
    async def get_model(id_):
        record = env.storage.get_record_by_id(id_)
        if record is None:
            return {'message': f'Model with {id_} not found.'}
        else:
            return map_record_to_dict(record)

    @app.get('/mo/display-options')
    async def get_display_options():
        return {
            'card_width': env.card_width(),
            'card_height': env.card_height(),
            'theme': env.theme()
        }

    logger.debug('MO API initialized')
