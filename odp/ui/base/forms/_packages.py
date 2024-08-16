from wtforms import FileField, SelectField, StringField
from wtforms.validators import data_required, input_required

from odp.ui.base.forms import BaseForm
from odp.ui.base.forms.validators import file_required


class PackageCreateForm(BaseForm):
    provider_id = SelectField(
        label='Package provider',
        validators=[input_required()],
    )
    title = StringField(
        label='Package title',
        validators=[data_required()],
    )


class ResourceUploadForm(BaseForm):
    title = StringField(
        label='Resource title',
        validators=[data_required()],
    )
    description = StringField(
        label='Resource description',
    )
    file = FileField(
        label='File upload',
        validators=[file_required()],
    )
