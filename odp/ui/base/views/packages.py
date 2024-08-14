from flask import Blueprint, flash, redirect, render_template, request, url_for

from odp.const import ODPPackageTag, ODPScope
from odp.lib.client import ODPAPIError
from odp.ui.base import api
from odp.ui.base.forms import ContributorTagForm, DOITagForm, PackageCreateForm
from odp.ui.base.lib import tags, utils
from odp.ui.base.templates import Button, ButtonTheme, create_btn

bp = Blueprint('packages', __name__)


@bp.route('/')
@api.view(ODPScope.PACKAGE_READ)
def index():
    page = request.args.get('page', 1)
    packages = api.get('/package/', page=page)

    return render_template(
        'package_index.html',
        packages=packages,
        buttons=[
            create_btn(scope=ODPScope.PACKAGE_WRITE),
        ]
    )


@bp.route('/<id>', methods=('GET', 'POST'))
@api.view(ODPScope.PACKAGE_READ)
def detail(id):
    package = api.get(f'/package/{id}')
    resources = utils.pagify(package['resources'])
    active_tab_id = request.args.get('tab', 'summary')

    doi_tag = tags.get_tag_instance(package, ODPPackageTag.DOI)
    doi_form = None

    contrib_tags = tags.get_tag_instances(package, ODPPackageTag.CONTRIBUTOR)
    contrib_form = None

    if active_modal_id := request.args.get('modal'):
        if request.method == 'POST':
            if active_modal_id == 'tag-doi':
                doi_form = DOITagForm(request.form)
                doi_form.validate()
            elif active_modal_id == 'tag-contributor':
                contrib_form = ContributorTagForm(request.form)
                contrib_form.validate()
        else:
            active_modal_id = None

    if not doi_form:
        doi_form = DOITagForm(data=doi_tag['data'] if doi_tag else None)

    if not contrib_form:
        contrib_form = ContributorTagForm()

    utils.populate_affiliation_choices(contrib_form.affiliations)

    doi_btn = Button(
        label='Set DOI',
        endpoint='.tag_doi',
        theme=ButtonTheme.info,
        object_id=id,
        scope=ODPScope.PACKAGE_DOI,
    )

    contrib_btn = Button(
        label='Add Contributor',
        endpoint='.tag_contributor',
        theme=ButtonTheme.success,
        object_id=id,
        scope=ODPScope.PACKAGE_WRITE,
    )

    return render_template(
        'package_detail.html',
        package=package,
        resources=resources,
        active_tab_id=active_tab_id,
        active_modal_id=active_modal_id,
        doi_tag=doi_tag,
        doi_btn=doi_btn,
        doi_form=doi_form,
        contrib_tags=contrib_tags,
        contrib_btn=contrib_btn,
        contrib_form=contrib_form,
    )


@bp.route('/new', methods=('GET', 'POST'))
@api.view(ODPScope.PACKAGE_WRITE)
def create():
    form = PackageCreateForm(request.form)
    utils.populate_provider_choices(form.provider_id)

    if request.method == 'POST' and form.validate():
        try:
            package = api.post('/package/', dict(
                provider_id=form.provider_id.data,
                title=(title := form.title.data),
                resource_ids=[],
            ))
            flash(f'Package <b>{title}</b> has been created.', category='success')
            return redirect(url_for('.detail', id=package['id']))

        except ODPAPIError as e:
            if response := api.handle_error(e):
                return response

    return render_template(
        'package_edit.html',
        form=form,
    )


@bp.route('/<id>/tag/doi', methods=('POST',))
@api.view(ODPScope.PACKAGE_DOI)
def tag_doi(id):
    form = DOITagForm(request.form)
    if form.validate():
        try:
            api.post(f'/package/{id}/tag', dict(
                tag_id=ODPPackageTag.DOI,
                data={
                    'doi': form.doi.data,
                },
            ))
            flash(f'{ODPPackageTag.DOI} tag has been set.', category='success')
            return redirect(url_for('.detail', id=id))

        except ODPAPIError as e:
            if response := api.handle_error(e):
                return response

    return redirect(url_for('.detail', id=id, tab='summary', modal='tag-doi'), code=307)


@bp.route('/<id>/tag/contributor', methods=('POST',))
@api.view(ODPScope.PACKAGE_WRITE)
def tag_contributor(id):
    form = ContributorTagForm(request.form)
    utils.populate_affiliation_choices(form.affiliations)

    if form.validate():
        try:
            api.post(f'/package/{id}/tag', dict(
                tag_id=ODPPackageTag.CONTRIBUTOR,
                data={
                    'name': form.name.data,
                    'orcid': form.orcid.data,
                    'is_author': form.is_author.data,
                    'role': form.author_role.data if form.is_author.data else form.contributor_role.data,
                    'affiliations': form.affiliations.data,
                },
            ))
            flash(f'{ODPPackageTag.CONTRIBUTOR} tag has been set.', category='success')
            return redirect(url_for('.detail', id=id))

        except ODPAPIError as e:
            if response := api.handle_error(e):
                return response

    return redirect(url_for('.detail', id=id, tab='contributors', modal='tag-contributor'), code=307)


@bp.route('/<id>/untag/doi/<tag_instance_id>', methods=('POST',))
@api.view(ODPScope.PACKAGE_DOI)
def untag_doi(id, tag_instance_id):
    return


@bp.route('/<id>/untag/contributor/<tag_instance_id>', methods=('POST',))
@api.view(ODPScope.PACKAGE_WRITE)
def untag_contributor(id, tag_instance_id):
    return
