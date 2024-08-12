import re

from wtforms import BooleanField, FloatField, SelectField, StringField
from wtforms.validators import input_required, optional

from odp.ui.base.forms import BaseForm
from odp.ui.base.forms.fields import DateStringField


class CatalogSearchForm(BaseForm):
    q = StringField(filters=[lambda s: s.strip() if s else s])
    n = FloatField()
    e = FloatField()
    s = FloatField()
    w = FloatField()
    after = DateStringField(validators=[optional()], label='Start date')
    before = DateStringField(validators=[optional()], label='End date')
    exclusive_region = BooleanField(label='Exclusive region')
    exclusive_interval = BooleanField(label='Exclusive interval')
    sort = SelectField(choices=[
        ('rank desc', 'Relevance'),
        ('timestamp desc', 'Last updated'),
    ])

    @classmethod
    def add_facets(cls, *facets: str) -> None:
        """Add facet fields to the search form."""
        for facet in facets:
            setattr(cls, cls.facet_fieldname(facet), StringField())

    @staticmethod
    def facet_fieldname(facet: str) -> str:
        return 'facet_' + re.sub(r'\W', '_', facet).lower()


class ResourceSearchForm(BaseForm):
    # disambiguate from the package's provider_id which might be on the same page
    resource_provider_id = SelectField(
        label='Provider',
        validators=[input_required()],
    )
    include_packaged = BooleanField(
        label='Show already-packaged resources',
    )
