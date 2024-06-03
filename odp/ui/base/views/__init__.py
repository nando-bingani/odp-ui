from flask import Flask

from odp.ui.base.forms import CatalogSearchForm


def init_app(app: Flask):
    if facets := app.config.get('CATALOG_FACETS'):
        CatalogSearchForm.add_facets(*facets)
