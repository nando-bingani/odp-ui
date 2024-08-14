from wtforms import SelectField, StringField
from wtforms.validators import data_required, input_required

from odp.ui.base.forms import BaseForm


class PackageCreateForm(BaseForm):
    provider_id = SelectField(
        label='Package provider',
        validators=[input_required()],
    )
    title = StringField(
        label='Package title',
        validators=[data_required()],
    )
