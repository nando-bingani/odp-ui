from wtforms import StringField
from wtforms.validators import data_required, length, regexp

from odp.const import ROR_PATH
from odp.ui.base.forms import BaseForm


class InstitutionKeywordForm(BaseForm):
    key = StringField(
        label='Full name of the institution',
        filters=[lambda s: s.strip() if s else s],
        validators=[data_required(), length(min=2)],
    )
    abbr = StringField(
        label='Acronym or abbreviated form of the institution name',
    )
    ror = StringField(
        label='Research Organization Registry (ROR) identifier',
        validators=[regexp(f'^(|{ROR_PATH})$', message='Expecting 9-character ROR.')],
        description='https://ror.org/',
    )
