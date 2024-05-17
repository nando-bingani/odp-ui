import json
from datetime import datetime

from wtforms import DateField, SelectMultipleField, TextAreaField
from wtforms.widgets import CheckboxInput, ListWidget


class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

    def __init__(self, *args, **kwargs):
        """Set dynamic_choices=True for multi-select fields that are
        dynamically populated in the browser. This causes the normal
        choices validation to be skipped."""
        self.dynamic_choices = kwargs.pop('dynamic_choices', False)
        super().__init__(*args, **kwargs)

    def pre_validate(self, form):
        if self.dynamic_choices:
            return

        super().pre_validate(form)


class StringListField(TextAreaField):
    def process_data(self, value):
        self.data = '\n'.join(value) if value is not None else None


class DateStringField(DateField):
    def process_data(self, value):
        self.data = datetime.strptime(value, '%Y-%m-%d') if value is not None else None


class JSONTextField(TextAreaField):
    def process_data(self, value):
        self.data = json.dumps(value, indent=4, ensure_ascii=False)
