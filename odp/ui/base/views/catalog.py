from flask import Blueprint, current_app, redirect, render_template, request, url_for

from odp.ui.base import cli
from odp.ui.base.forms import SearchForm

bp = Blueprint('catalog', __name__)


@bp.route('/')
def index():
    page = request.args.get('page', 1)
    text_query = request.args.get('text_query')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    filter_ = ''
    if text_query:
        filter_ += f'&text_query={text_query}'
    if start_date:
        filter_ += f'&start_date={start_date}'
    if end_date:
        filter_ += f'&end_date={end_date}'

    catalog_id = current_app.config['CATALOG_ID']
    records = cli.get(f'/catalog/{catalog_id}/records?page={page}{filter_}')
    return render_template(
        'catalog_index.html',
        records=records,
        filter_=filter_,
        search_form=SearchForm(request.args),
    )


@bp.route('/search', methods=('POST',))
def search():
    form = SearchForm(request.form)
    query = {}
    if form.text_query.data:
        query |= dict(text_query=form.text_query.data)
    if form.start_date.data:
        query |= dict(start_date=form.start_date.data)
    if form.end_date.data:
        query |= dict(end_date=form.end_date.data)

    return redirect(url_for('.index', **query))


@bp.route('/<path:id>')
def view(id):
    catalog_id = current_app.config['CATALOG_ID']
    record = cli.get(f'/catalog/{catalog_id}/records/{id}')
    return render_template(
        'catalog_record.html',
        record=record,
    )
