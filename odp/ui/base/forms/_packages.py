from wtforms import FileField, SelectField, StringField, ValidationError
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


class FileUploadForm(BaseForm):
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


class ZipUploadForm(BaseForm):
    zip_file = FileField(
        label='File upload',
        validators=[file_required()],
    )
    zip_size = StringField(
        label='File size',
        render_kw={'readonly': ''},
    )
    zip_mimetype = StringField(
        label='Content type',
        render_kw={'readonly': ''},
    )
    zip_sha256 = StringField(
        label='SHA-256 checksum',
        render_kw={'readonly': ''},
    )

    def validate_zip_file(self, field):
        if self.zip_mimetype.data != 'application/zip':
            raise ValidationError('Only .zip files are supported for zip upload')
