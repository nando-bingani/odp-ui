import json

from flask import Blueprint, current_app, redirect, render_template, request, url_for

from odp.ui.base import cli
from odp.ui.base.forms import SearchForm

bp = Blueprint('catalog', __name__)


@bp.route('/')
@cli.view()
def index():
    catalog_id = current_app.config['CATALOG_ID']
    facets = current_app.config['CATALOG_FACETS']

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

    facet_api_query = {}
    facet_ui_query = {}
    facet_fields = {}
    for facet_title in facets:
        facet_field = SearchForm.facet_fieldname(facet_title)
        facet_fields[facet_title] = facet_field
        if facet_value := request.args.get(facet_field):
            facet_api_query[facet_title] = facet_value
            facet_ui_query[facet_field] = facet_value

    result = cli.get(
        f'/catalog/{catalog_id}/search',
        text_query=text_query,
        facet_query=json.dumps(facet_api_query),
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

    return render_template(
        'catalog_index.html',
        form=SearchForm(request.args),
        result=result,
        facet_fields=facet_fields,
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

    facets = current_app.config['CATALOG_FACETS']
    for facet_title in facets:
        if not query[facet_field := SearchForm.facet_fieldname(facet_title)]:
            query.pop(facet_field)

    return redirect(url_for('.index', **query))


@bp.route('/<path:id>')
@cli.view()
def view(id):
    catalog_id = current_app.config['CATALOG_ID']
    terms_of_use = current_app.config['CATALOG_TERMS_OF_USE']

    record = cli.get(f'/catalog/{catalog_id}/records/{id}')

    return render_template(
        'catalog_record.html',
        record=record,
        terms_of_use=terms_of_use,
    )
