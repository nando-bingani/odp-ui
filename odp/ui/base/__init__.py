from pathlib import Path

import redis
from flask import Flask

from odp.config import config
from odp.ui.base import forms, templates
from odp.ui.client import ODPUIClient

STATIC_DIR = Path(__file__).parent / 'static'
TEMPLATE_DIR = Path(__file__).parent / 'templates'

api: ODPUIClient


def init_app(app: Flask, *, is_odp_client: bool = True):
    if is_odp_client:
        global api
        api = ODPUIClient(
            api_url=app.config['API_URL'],
            hydra_url=config.HYDRA.PUBLIC.URL,
            client_id=app.config['CLIENT_ID'],
            client_secret=app.config['CLIENT_SECRET'],
            scope=app.config['CLIENT_SCOPE'],
            cache=redis.Redis(
                host=config.REDIS.HOST,
                port=config.REDIS.PORT,
                db=config.REDIS.DB,
                decode_responses=True,
            ),
            app=app,
        )

    forms.init_app(app)
    templates.init_app(app)
