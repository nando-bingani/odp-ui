import json

from flask import request
from werkzeug.utils import secure_filename
from wtforms import ValidationError


def json_object(form, field):
    """A JSONTextField validator that ensures the value is a JSON object."""
    try:
        obj = json.loads(field.data)
        if not isinstance(obj, dict):
            raise ValidationError('The value must be a JSON object.')
    except json.JSONDecodeError:
        raise ValidationError('Invalid JSON')


def file_required(message='Please select a file.'):
    """A FileField validator that ensures that a file is selected."""

    def validator(form, field):
        if not (file := request.files.get(field.id)) or not secure_filename(file.filename):
            raise ValidationError(message)

    return validator
