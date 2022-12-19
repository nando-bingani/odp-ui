import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from functools import partial
from zoneinfo import ZoneInfo

from flask import Flask


def init_app(app: Flask):
    @app.template_filter()
    def format_json(obj):
        return json.dumps(obj, indent=4, ensure_ascii=False)

    @app.template_filter()
    def timestamp(value):
        dt = datetime.fromisoformat(value).astimezone(ZoneInfo('Africa/Johannesburg'))
        return dt.strftime('%d %b %Y, %H:%M %Z')

    @app.template_filter()
    def date(value):
        dt = datetime.fromisoformat(value).astimezone(ZoneInfo('Africa/Johannesburg'))
        return dt.strftime('%d %b %Y')


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
