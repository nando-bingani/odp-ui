from wtforms import BooleanField, FloatField, HiddenField, RadioField, SelectField, StringField, ValidationError
from wtforms.validators import data_required, input_required, number_range, optional, regexp

from odp.const import DOI_REGEX, ORCID_PATH
from odp.ui.base.forms import BaseForm
from odp.ui.base.forms.fields import DateStringField, DynamicSelectField, MultiCheckboxField
from odp.ui.base.forms.validators import pseudo_required


class DOITagForm(BaseForm):
    doi = StringField(
        label='DOI',
        validators=[data_required(), regexp(DOI_REGEX)],
    )


class TitleTagForm(BaseForm):
    title = StringField(
        label='Package title',
        validators=[data_required()],
    )


class SDGTagForm(BaseForm):
    goal = DynamicSelectField(
        label='Goal',
        validators=[input_required()],
    )
    target = DynamicSelectField(
        label='Target',
    )
    indicator = DynamicSelectField(
        label='Indicator',
    )
    comment = StringField(
        label='Comment',
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
        validators=[regexp(f'^(|{ORCID_PATH})$', message='Expecting 16-digit ORCID. Example: 0000-0001-2345-678X')],
        description='https://orcid.org/',
    )
    is_author = BooleanField(
        label='Author',
        description='Check this box if the contributor must be cited as an author of the data package.',
    )
    author_role = SelectField(
        label='Role',
        choices=[
            ('', 'Please select...'),
            ('originator', 'Originator'),
            ('principalInvestigator', 'Principal Investigator'),
        ],
        validate_choice=False,
        validators=[pseudo_required()],
    )
    contributor_role = SelectField(
        label='Role',
        choices=[
            ('', 'Please select...'),
            ('custodian', 'Custodian'),
            ('distributor', 'Distributor'),
            ('owner', 'Owner'),
            ('pointOfContact', 'Point Of Contact'),
            ('processor', 'Processor'),
            ('resourceProvider', 'Resource Provider'),
        ],
        validate_choice=False,
        validators=[pseudo_required()],
    )
    affiliations = MultiCheckboxField(
        label='Affiliation(s)',
        description='Click the Add Institution button if your institution is not listed here.',
    )
    contact_info = StringField(
        label='Contact information',
        validators=[pseudo_required()],
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
        validators=[number_range(min=-180, max=180), optional(), pseudo_required()],
    )
    east = FloatField(
        label='East',
        validators=[number_range(min=-180, max=180), input_required()],
    )
    south = FloatField(
        label='South',
        validators=[number_range(min=-90, max=90), optional(), pseudo_required()],
    )
    north = FloatField(
        label='North',
        validators=[number_range(min=-90, max=90), input_required()],
    )

    def validate_shape(self, field):
        if field.data == 'box':
            if self.west.data is None or self.south.data is None:
                raise ValidationError('All coordinates are required for a bounding box')

    def validate_west(self, field):
        if field.data is not None and field.data > self.east.data:
            raise ValidationError('West must be less than or equal to East')

    def validate_south(self, field):
        if field.data is not None and field.data > self.north.data:
            raise ValidationError('South must be less than or equal to North')


class DateRangeTagForm(BaseForm):
    start = DateStringField(
        label='Start date',
        validators=[input_required()],
    )
    end = DateStringField(
        label='End date',
        validators=[input_required()],
    )

    def validate_end(self, field):
        if field.data < self.start.data:
            raise ValidationError('The end date cannot be earlier than the start date.')


class AbstractTagForm(BaseForm):
    abstract_hidden = HiddenField(
        label='Abstract',
        validators=[data_required()],
    )


class LineageTagForm(BaseForm):
    lineage_hidden = HiddenField(
        label='Methods (Lineage)',
        validators=[data_required()],
    )
