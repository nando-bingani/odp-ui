import json

from flask import request
from werkzeug.utils import secure_filename
from wtforms import ValidationError


def json_object():
    """A JSONTextField validator that ensures the value is a JSON object."""

    def validator(form, field):
        try:
            obj = json.loads(field.data)
            if not isinstance(obj, dict):
                raise ValidationError('The value must be a JSON object.')
        except json.JSONDecodeError:
            raise ValidationError('Invalid JSON')

    return validator


class FileRequired:
    """A FileField validator that ensures that a file is selected."""

    def __init__(self, message='Please select a file.'):
        self.message = message
        self.field_flags = {'required': True}

    def __call__(self, form, field):
        if not (file := request.files.get(field.id)) or not secure_filename(file.filename):
            raise ValidationError(self.message)


class PseudoRequired:
    """A validator that makes the field appear required without
    affecting server-side form validation."""

    def __init__(self):
        self.field_flags = {'required': True}

    def __call__(self, form, field):
        pass


file_required = FileRequired
pseudo_required = PseudoRequired
