from flask import Blueprint, current_app, redirect, render_template, request, url_for

from odp.ui.base import cli
from odp.ui.base.forms import SearchForm

bp = Blueprint('catalog', __name__)


@bp.route('/')
@cli.view()
def index():
    catalog_id = current_app.config['CATALOG_ID']
    text_query = request.args.get('q')
    north_bound = request.args.get('n')
    east_bound = request.args.get('e')
    south_bound = request.args.get('s')
    west_bound = request.args.get('w')
    start_date = request.args.get('after')
    end_date = request.args.get('before')
    exclusive_region = request.args.get('exclusive_region')
    exclusive_interval = request.args.get('exclusive_interval')
    page = request.args.get('page', 1)

    result = cli.get(
        f'/catalog/{catalog_id}/search',
        text_query=text_query,
        north_bound=north_bound,
        east_bound=east_bound,
        south_bound=south_bound,
        west_bound=west_bound,
        start_date=start_date,
        end_date=end_date,
        exclusive_region=exclusive_region,
        exclusive_interval=exclusive_interval,
        include_nonsearchable=False,
        page=page,
    )

    query = ''
    if text_query:
        query += f'&q={text_query}'
    if north_bound:
        query += f'&n={north_bound}'
    if east_bound:
        query += f'&e={east_bound}'
    if south_bound:
        query += f'&s={south_bound}'
    if west_bound:
        query += f'&w={west_bound}'
    if start_date:
        query += f'&after={start_date}'
    if end_date:
        query += f'&before={end_date}'
    if exclusive_region:
        query += '&exclusive_region=True'
    if exclusive_interval:
        query += '&exclusive_interval=True'

    return render_template(
        'catalog_index.html',
        form=SearchForm(request.args),
        query=query,
        result=result,
        facets=current_app.config['CATALOG_FACETS'],
    )


@bp.route('/search', methods=('POST',))
def search():
    form = SearchForm(request.form)
    query = form.data
    query.pop('csrf_token')
    if not query['exclusive_region']:
        query.pop('exclusive_region')
    if not query['exclusive_interval']:
        query.pop('exclusive_interval')
    return redirect(url_for('.index', **query))


@bp.route('/<path:id>')
@cli.view()
def view(id):
    catalog_id = current_app.config['CATALOG_ID']
    record = cli.get(f'/catalog/{catalog_id}/records/{id}')
    return render_template(
        'catalog_record.html',
        record=record,
    )
