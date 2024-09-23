from wtforms import FileField, SelectField, StringField
from wtforms.validators import data_required, input_required

from odp.ui.base.forms import BaseForm
from odp.ui.base.forms.validators import file_required


class PackageForm(BaseForm):
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
    )
    description = StringField(
        label='Resource description',
    )
    file = FileField(
        label='File upload',
        validators=[file_required()],
    )
    size = StringField(
        label='File size',
        render_kw={'readonly': ''},
    )
    mimetype = StringField(
        label='Content type',
        render_kw={'readonly': ''},
    )
    sha256 = StringField(
        label='SHA-256 checksum',
        render_kw={'readonly': ''},
    )
