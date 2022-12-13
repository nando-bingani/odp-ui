from flask import Blueprint, current_app, render_template, request

from odp.ui.base import cli
from odp.ui.base.forms import SearchForm

bp = Blueprint('catalog', __name__)


@bp.route('/')
def index():
    page = request.args.get('page', 1)
    text_q = request.args.get('q')

    api_filter = ''
    ui_filter = ''
    if text_q:
        api_filter += f'&text_q={text_q}'
        ui_filter += f'&q={text_q}'

    catalog_id = current_app.config['CATALOG_ID']
    records = cli.get(f'/catalog/{catalog_id}/records?page={page}{api_filter}')
    return render_template(
        'catalog_index.html',
        records=records,
        filter_=ui_filter,
        search_form=SearchForm(request.args),
    )


@bp.route('/<path:id>')
def view(id):
    catalog_id = current_app.config['CATALOG_ID']
    record = cli.get(f'/catalog/{catalog_id}/records/{id}')
    return render_template(
        'catalog_record.html',
        record=record,
    )
