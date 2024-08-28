from wtforms import BooleanField, FloatField, RadioField, SelectField, StringField, ValidationError
from wtforms.validators import data_required, input_required, number_range, optional, regexp

from odp.const import DOI_REGEX
from odp.ui.base.forms import BaseForm
from odp.ui.base.forms.fields import MultiCheckboxField


class DOITagForm(BaseForm):
    doi = StringField(
        label='DOI',
        validators=[data_required(), regexp(DOI_REGEX)],
    )


class KeywordTagForm(BaseForm):
    vocabulary = StringField(
        label='Vocabulary',
        render_kw={'readonly': ''},
    )
    keyword = SelectField(
        label='Keyword',
        validators=[input_required()],
    )
    comment = StringField(
        label='Comment',
    )


class ContributorTagForm(BaseForm):
    name = StringField(
        label='Full name',
        validators=[data_required()],
    )
    orcid = StringField(
        label='ORCID',
    )
    is_author = BooleanField(
        label='Author',
        description='Check this box if the contributor must be cited as an author of the data package.',
    )
    author_role = SelectField(
        label='Role',
        choices=[
            'originator',
            'principalInvestigator',
        ],
    )
    contributor_role = SelectField(
        label='Role',
        choices=[
            "resourceProvider",
            "custodian",
            "owner",
            "distributor",
            "pointOfContact",
            "processor"
        ],
    )
    affiliations = MultiCheckboxField(
        label='Affiliation(s)',
        description='Click the Add Institution button if your institution is not listed here.',
    )


class GeoLocationTagForm(BaseForm):
    place = StringField(
        label='Place name',
        validators=[data_required()],
    )
    shape = RadioField(
        label='Shape',
        choices=[
            ('point', 'Point location'),
            ('box', 'Geographic region'),
        ],
    )
    west = FloatField(
        label='West',
        validators=[number_range(min=-180, max=180), optional()],
    )
    east = FloatField(
        label='East',
        validators=[number_range(min=-180, max=180), input_required()],
    )
    south = FloatField(
        label='South',
        validators=[number_range(min=-90, max=90), optional()],
    )
    north = FloatField(
        label='North',
        validators=[number_range(min=-90, max=90), input_required()],
    )

    def validate_shape(self, field):
        if field.data == 'box':
            if self['west'].data is None or self['south'].data is None:
                raise ValidationError('All coordinates are required for a bounding box')

    def validate_west(self, field):
        if field.data is not None and field.data > self['east'].data:
            raise ValidationError('West must be less than or equal to East')

    def validate_south(self, field):
        if field.data is not None and field.data > self['north'].data:
            raise ValidationError('South must be less than or equal to North')
