from wtforms import StringField
from wtforms.validators import data_required, length, regexp

from odp.const import ROR_REGEX
from odp.ui.base.forms import BaseForm


class InstitutionKeywordForm(BaseForm):
    title = StringField(
        label='Institution title',
        filters=[lambda s: s.strip() if s else s],
        validators=[data_required(), length(min=2)],
    )
    abbr = StringField(
        label='Acronym / short title',
        validators=[data_required()],
    )
    ror = StringField(
        label='ROR (Research Organization Registry) identifier',
        validators=[regexp('^$|' + ROR_REGEX)],
        description='The entire URL i.e. https://ror.org/...'
    )
