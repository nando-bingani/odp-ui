from pathlib import Path

import redis
from flask import Flask

from odp.client import ODPClient
from odp.config import config
from odp.ui.base import forms, templates
from odp.ui.client import ODPUIClient
from odp.version import VERSION

STATIC_DIR = Path(__file__).parent / 'static'
TEMPLATE_DIR = Path(__file__).parent / 'templates'

api: ODPUIClient
"""ODP client for user-authenticated API access."""

cli: ODPClient
"""ODP client for client-authenticated API access."""


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

        # TODO: we might want to support using a distinct client, with its
        #  own (limited) scope, for client-credentials access to the API
        #  from a UI application
        global cli
        cli = ODPClient(
            api_url=app.config['API_URL'],
            hydra_url=config.HYDRA.PUBLIC.URL,
            client_id=app.config['CLIENT_ID'],
            client_secret=app.config['CLIENT_SECRET'],
            scope=app.config['CLIENT_SCOPE'],
        )

    forms.init_app(app)
    templates.init_app(app)

    app.config.update(ODP_VERSION=VERSION)
