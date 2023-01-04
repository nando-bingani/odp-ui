from flask import Blueprint, current_app, redirect, render_template, request, url_for

from odp.ui.base import cli
from odp.ui.base.forms import SearchForm

bp = Blueprint('catalog', __name__)


@bp.route('/')
def index():
    catalog_id = current_app.config['CATALOG_ID']
    text_query = request.args.get('q')
    start_date = request.args.get('after')
    end_date = request.args.get('before')
    page = request.args.get('page', 1)

    records = cli.get(
        f'/catalog/{catalog_id}/records',
        text_query=text_query,
        start_date=start_date,
        end_date=end_date,
        page=page,
    )

    filter_ = ''
    if text_query:
        filter_ += f'&q={text_query}'
    if start_date:
        filter_ += f'&after={start_date}'
    if end_date:
        filter_ += f'&before={end_date}'

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
    if form.q.data:
        query |= dict(q=form.q.data)
    if form.after.data:
        query |= dict(after=form.after.data)
    if form.before.data:
        query |= dict(before=form.before.data)

    return redirect(url_for('.index', **query))


@bp.route('/<path:id>')
def view(id):
    catalog_id = current_app.config['CATALOG_ID']
    record = cli.get(f'/catalog/{catalog_id}/records/{id}')
    return render_template(
        'catalog_record.html',
        record=record,
    )
