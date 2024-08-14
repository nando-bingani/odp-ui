from wtforms import BooleanField, SelectField, StringField
from wtforms.validators import data_required, input_required, regexp

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
