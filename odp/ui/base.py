from pathlib import Path

import redis
from flask import Flask
from flask_login import LoginManager

from odp.config import config
from odp.ui.client import ODPUIClient

STATIC_DIR = Path(__file__).parent / 'static'
TEMPLATE_DIR = Path(__file__).parent / 'templates'

login_manager = LoginManager()

odp_ui_client: ODPUIClient


def init_app(app: Flask):
    from odp.ui import api, forms, templates

    global odp_ui_client
    odp_ui_client = ODPUIClient(
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

    api.init_app(app)
    forms.init_app(app)
    templates.init_app(app)
    login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return odp_ui_client.get_user(user_id)
