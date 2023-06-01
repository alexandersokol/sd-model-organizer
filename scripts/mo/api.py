from fastapi import FastAPI

from scripts.mo.environment import logger, env


def init_extension_api(app: FastAPI):
    @app.get('/mo/display-options')
    async def get_display_options():
        return {
            'card_width': env.card_width(),
            'card_height': env.card_height(),
            'theme': env.theme()
        }

    logger.debug('Model Organizer API initialized')
