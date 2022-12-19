from flask import Blueprint, current_app, render_template, request

from odp.ui.base import cli
from odp.ui.base.forms import SearchForm

bp = Blueprint('catalog', __name__)


@bp.route('/')
def index():
    page = request.args.get('page', 1)
    text_query = request.args.get('text_query')

    filter_ = ''
    if text_query:
        filter_ += f'&text_query={text_query}'

    catalog_id = current_app.config['CATALOG_ID']
    records = cli.get(f'/catalog/{catalog_id}/records?page={page}{filter_}')
    return render_template(
        'catalog_index.html',
        records=records,
        filter_=filter_,
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
