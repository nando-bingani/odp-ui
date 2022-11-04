from flask import Flask

from odp.ui.base.views import hydra


def init_app(app: Flask):
    app.register_blueprint(hydra.bp, url_prefix='/oauth2')
