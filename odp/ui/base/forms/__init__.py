from flask import Flask

from odp.ui.base.forms._base import BaseForm
from odp.ui.base.forms._keywords import InstitutionKeywordForm
from odp.ui.base.forms._packages import FileUploadForm, PackageForm, ZipUploadForm
from odp.ui.base.forms._search import CatalogSearchForm, ResourceSearchForm
from odp.ui.base.forms._tags import ContributorTagForm, DOITagForm, DateRangeTagForm, GeoLocationTagForm, KeywordTagForm, SDGTagForm


def init_app(app: Flask):
    BaseForm.Meta.csrf_secret = bytes(app.config['SECRET_KEY'], 'utf-8')
