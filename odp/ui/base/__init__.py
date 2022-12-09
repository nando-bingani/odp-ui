from pathlib import Path

import redis
from flask import Flask
from jinja2 import ChoiceLoader, FileSystemLoader
from werkzeug.middleware.proxy_fix import ProxyFix

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


def init_app(
        app: Flask,
        *,
        user_api: bool = False,
        client_api: bool = False,
        template_dir: Path,
):
    """Base initialization for an ODP UI application.

    :param app: Flask app instance
    :param user_api: create an ODP client (`api`) for user-authenticated API access
    :param client_api: create an ODP client (`cli`) for client-authenticated API access
    :param template_dir: the app's local template directory
    """
    app.config.update(
        ODP_VERSION=VERSION,
        SESSION_COOKIE_SAMESITE='Lax',
        SESSION_COOKIE_SECURE=True,
    )

    if user_api:
        global api
        api = ODPUIClient(
            api_url=config.ODP.API_URL,
            hydra_url=config.HYDRA.PUBLIC.URL,
            client_id=app.config['UI_CLIENT_ID'],
            client_secret=app.config['UI_CLIENT_SECRET'],
            scope=app.config['UI_CLIENT_SCOPE'],
            cache=redis.Redis(
                host=config.REDIS.HOST,
                port=config.REDIS.PORT,
                db=config.REDIS.DB,
                decode_responses=True,
            ),
            app=app,
        )

    if client_api:
        global cli
        cli = ODPClient(
            api_url=config.ODP.API_URL,
            hydra_url=config.HYDRA.PUBLIC.URL,
            client_id=app.config['SI_CLIENT_ID'],
            client_secret=app.config['SI_CLIENT_SECRET'],
            scope=app.config['SI_CLIENT_SCOPE'],
        )

    app.jinja_loader = ChoiceLoader([
        FileSystemLoader(template_dir),
        FileSystemLoader(TEMPLATE_DIR),
    ])
    app.static_folder = STATIC_DIR

    forms.init_app(app)
    templates.init_app(app)

    # trust the X-Forwarded-* headers set by the proxy server
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_prefix=1)
