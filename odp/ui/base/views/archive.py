from flask import Blueprint, current_app, render_template, request

from odp.const import ODPScope
from odp.ui.base import api

bp = Blueprint('archive', __name__)


@bp.route('/')
@api.view(ODPScope.ARCHIVE_READ)
def index():
    archive_id = current_app.config['ARCHIVE_ID']
    page = request.args.get('page', 1)
    resources = api.get(f'/archive/{archive_id}/resources', page=page)
    return render_template(
        'archive_index.html',
        resources=resources,
    )
