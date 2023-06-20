import os

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

    @app.get('/mo/thumbnail')
    async def get_thumbnail_file(filename: str = ""):
        from starlette.responses import FileResponse

        ext = os.path.splitext(filename)[1].lower()
        if ext not in (".png", ".jpg", ".jpeg", ".webp"):
            raise ValueError(f"File cannot be fetched: {filename}. Only png and jpg and jpeg and webp.")

        return FileResponse(filename, headers={"Accept-Ranges": "bytes"})

    logger.debug('Model Organizer API initialized')
