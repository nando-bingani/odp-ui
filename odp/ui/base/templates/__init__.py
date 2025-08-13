import json
import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from functools import partial
from typing import Any
from zoneinfo import ZoneInfo

from flask import Flask

from odp.const import DOI_REGEX


def init_app(app: Flask):
    """Set up common template filters."""

    @app.template_filter()
    def format_json(obj: Any) -> str:
        """Return nicely formatted JSON."""
        return json.dumps(obj, indent=4, ensure_ascii=False)

    @app.template_filter()
    def timestamp(value: str) -> str:
        """Return a nicely formatted timestamp from an ISO 8601 datetime string."""
        if not value:
            return ''
        dt = datetime.fromisoformat(value).astimezone(ZoneInfo('Africa/Johannesburg'))
        return dt.strftime('%d %b %Y, %H:%M %Z')

    @app.template_filter()
    def date(value: str) -> str:
        """Return a nicely formatted date from an ISO 8601 datetime string."""
        if not value:
            return ''
        dt = datetime.fromisoformat(value).astimezone(ZoneInfo('Africa/Johannesburg'))
        return dt.strftime('%d %b %Y')

    @app.template_filter()
    def uncamel(value: str) -> str:
        """Format a camel-cased value as a title string.
        e.g. 'IsDescribedBy' becomes 'Is Described By'
             'pointOfContact' becomes 'Point Of Contact'
        """
        value = value[0].upper() + value[1:]
        return ' '.join(re.findall('[A-Z][a-z]*', value))

    @app.template_filter()
    def datacite_enum(value: str) -> str:
        """Format a DataCite enum value as a title string.
        e.g. 'IsDescribedBy' becomes 'Is Described By'"""
        return ' '.join(re.findall('[A-Z][a-z]*', value))

    @app.template_filter()
    def doi(value: str) -> str | None:
        """Pull a DOI out of `value`."""
        if match := re.search(DOI_REGEX[1:], value):
            return match.group(0)


class ButtonTheme(str, Enum):
    primary = 'primary'
    secondary = 'secondary'
    info = 'info'
    success = 'success'
    warning = 'warning'
    danger = 'danger'
    light = 'light'
    dark = 'dark'


@dataclass
class Button:
    label: str
    endpoint: str
    theme: ButtonTheme
    outline: bool = True
    prompt: str = None
    prompt_args: tuple = ()
    object_id: str = None
    enabled: bool = True


create_btn = partial(
    Button,
    label='Create',
    endpoint='.create',
    theme=ButtonTheme.success,
)

edit_btn = partial(
    Button,
    label='Edit',
    endpoint='.edit',
    theme=ButtonTheme.primary,
)

delete_btn = partial(
    Button,
    label='Delete',
    endpoint='.delete',
    theme=ButtonTheme.danger,
    prompt='Are you sure you want to delete %s? This cannot be undone!',
)
