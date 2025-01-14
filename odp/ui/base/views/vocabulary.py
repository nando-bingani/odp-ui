import json
import pathlib

from flask import Blueprint

import odp.vocab

bp = Blueprint('vocabulary', __name__)

vocab_dir = pathlib.Path(odp.vocab.__file__).parent


@bp.route('/<id>')
def get_json(id):
    """Return the JSON for a static vocabulary."""
    with open(vocab_dir / f'{id.lower()}.json') as f:
        return json.load(f)
