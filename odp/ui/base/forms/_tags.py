from wtforms import BooleanField, DateTimeField, FieldList, FormField, SelectField, StringField
from wtforms.validators import data_required, input_required, regexp

from odp.const import DOI_REGEX
from odp.ui.base.forms import BaseForm
from odp.ui.base.forms._keywords import InstitutionKeywordForm


class TagBaseForm(BaseForm):
    tag_id = StringField(
        label='Tag id',
        render_kw={'readonly': ''},
    )
    user_id = StringField(
        label='User id',
        render_kw={'readonly': ''},
    )
    user_name = StringField(
        label='User name',
        render_kw={'readonly': ''},
    )
    timestamp = DateTimeField(
        label='Timestamp',
        render_kw={'readonly': ''},
    )


class DOITagForm(TagBaseForm):
    doi = StringField(
        label='DOI',
        validators=[data_required(), regexp(DOI_REGEX)],
    )


class KeywordTagForm(TagBaseForm):
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


class ContributorTagForm(TagBaseForm):
    name = StringField(
        label='Name',
        validators=[data_required()],
    )
    orcid = SelectField(
        label='ORCID',
    )
    is_author = BooleanField(
        label='Cited author'
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
    affiliations = FieldList(SelectField(
        label='Affiliation'
    ))
    unlisted_affiliations = FieldList(FormField(
        InstitutionKeywordForm,
        label='Unlisted affiliation',
    ))
