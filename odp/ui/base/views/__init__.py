from flask import Flask

from odp.ui.base.forms import SearchForm


def init_app(app: Flask):
    if facets := app.config.get('CATALOG_FACETS'):
        SearchForm.add_facets(*facets)
