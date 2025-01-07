from flask import Blueprint, current_app, flash, g, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

from odp.const import ODPPackageTag, ODPScope, ODPVocabulary
from odp.lib.client import ODPAPIError
from odp.ui.base import api
from odp.ui.base.forms import (
    ContributorTagForm,
    DOITagForm,
    DateRangeTagForm,
    FileUploadForm,
    GeoLocationTagForm,
    InstitutionKeywordForm,
    PackageForm,
    ZipUploadForm,
)
from odp.ui.base.lib import tags, utils
from odp.ui.base.templates import Button, ButtonTheme, create_btn, edit_btn

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

    doi_tag = tags.get_tag_instance(package, ODPPackageTag.DOI)
    geoloc_tag = tags.get_tag_instance(package, ODPPackageTag.GEOLOCATION)
    daterange_tag = tags.get_tag_instance(package, ODPPackageTag.DATERANGE)
    contrib_tags = tags.get_tag_instances(package, ODPPackageTag.CONTRIBUTOR)

    doi_form = None
    geoloc_form = None
    daterange_form = None
    contrib_form = None
    institution_form = None
    file_form = None
    zip_form = None

    active_modal_reload_on_cancel = False
    if active_modal_id := request.args.get('modal'):
        if request.method == 'POST':
            if active_modal_id == 'tag-doi':
                doi_form = DOITagForm(request.form)
                doi_form.validate()
                active_modal_reload_on_cancel = doi_tag is not None
            elif active_modal_id == 'tag-geoloc':
                geoloc_form = GeoLocationTagForm(request.form)
                geoloc_form.validate()
                active_modal_reload_on_cancel = geoloc_tag is not None
            elif active_modal_id == 'tag-daterange':
                daterange_form = DateRangeTagForm(request.form)
                daterange_form.validate()
                active_modal_reload_on_cancel = daterange_tag is not None
            elif active_modal_id == 'tag-contributor':
                contrib_form = ContributorTagForm(request.form)
                contrib_form.validate()
            elif active_modal_id == 'add-institution':
                institution_form = InstitutionKeywordForm(request.form)
                institution_form.validate()
            elif active_modal_id == 'upload-file':
                file_form = FileUploadForm(request.form)
                file_form.validate()
            elif active_modal_id == 'upload-zip':
                zip_form = ZipUploadForm(request.form)
                zip_form.validate()
        else:
            active_modal_id = None

    if not doi_form:
        doi_form = DOITagForm(data=doi_tag['data'] if doi_tag else None)

    if not geoloc_form:
        geoloc_form = GeoLocationTagForm(data=geoloc_tag['data'] if geoloc_tag else None)

    if not daterange_form:
        daterange_form = DateRangeTagForm(data=daterange_tag['data'] if daterange_tag else None)

    if not contrib_form:
        contrib_form = ContributorTagForm()

    if not institution_form:
        institution_form = InstitutionKeywordForm()

    if not file_form:
        file_form = FileUploadForm()

    if not zip_form:
        zip_form = ZipUploadForm()

    utils.populate_keyword_choices(contrib_form.affiliations, ODPVocabulary.INSTITUTION, include_proposed=True)

    doi_btn = Button(
        label='Edit DOI' if doi_tag else 'Add DOI',
        endpoint='.tag_doi',
        theme=ButtonTheme.primary,
        object_id=id,
        scope=ODPScope.PACKAGE_DOI,
    )

    geoloc_btn = Button(
        label='Edit Geographic Location' if geoloc_tag else 'Add Geographic Location',
        endpoint='.tag_geolocation',
        theme=ButtonTheme.primary,
        object_id=id,
        scope=ODPScope.PACKAGE_WRITE,
    )

    daterange_btn = Button(
        label='Edit Temporal Extent' if daterange_tag else 'Add Temporal Extent',
        endpoint='.tag_daterange',
        theme=ButtonTheme.primary,
        object_id=id,
        scope=ODPScope.PACKAGE_WRITE,
    )

    contrib_btn = Button(
        label='Add Contributor',
        endpoint='.tag_contributor',
        theme=ButtonTheme.success,
        object_id=id,
        scope=ODPScope.PACKAGE_WRITE,
    )

    institution_btn = Button(
        label='Add Institution',
        endpoint='.add_institution',
        theme=ButtonTheme.info,
        object_id=id,
        scope=ODPScope.KEYWORD_SUGGEST,
        description='Add an unlisted institution to the list of available contributor affiliations.',
    )

    file_btn = Button(
        label='Upload File',
        endpoint='.upload_file',
        theme=ButtonTheme.warning,
        object_id=id,
        scope=ODPScope.PACKAGE_WRITE,
    )

    zip_btn = Button(
        label='Upload Zip',
        endpoint='.upload_zip',
        theme=ButtonTheme.warning,
        object_id=id,
        scope=ODPScope.PACKAGE_WRITE,
    )

    return render_template(
        'package_detail.html',
        package=package,
        resources=resources,
        active_modal_id=active_modal_id,
        active_modal_reload_on_cancel=active_modal_reload_on_cancel,
        can_edit=ODPScope.PACKAGE_WRITE in g.user_permissions,
        edit_btn=edit_btn(object_id=id, scope=ODPScope.PACKAGE_WRITE),
        doi_tag=doi_tag,
        doi_btn=doi_btn,
        doi_form=doi_form,
        geoloc_tag=geoloc_tag,
        geoloc_btn=geoloc_btn,
        geoloc_form=geoloc_form,
        daterange_tag=daterange_tag,
        daterange_btn=daterange_btn,
        daterange_form=daterange_form,
        contrib_tags=contrib_tags,
        contrib_btn=contrib_btn,
        contrib_form=contrib_form,
        institution_btn=institution_btn,
        institution_form=institution_form,
        file_btn=file_btn,
        file_form=file_form,
        zip_btn=zip_btn,
        zip_form=zip_form,
    )


@bp.route('/new', methods=('GET', 'POST'))
@api.view(ODPScope.PACKAGE_WRITE)
def create():
    form = PackageForm(request.form)
    utils.populate_provider_choices(form.provider_id)

    if request.method == 'POST' and form.validate():
        try:
            package = api.post('/package/', dict(
                provider_id=form.provider_id.data,
                title=(title := form.title.data),
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


@bp.route('/<id>/edit', methods=('GET', 'POST'))
@api.view(ODPScope.PACKAGE_WRITE)
def edit(id):
    package = api.get(f'/package/{id}')

    form = PackageForm(request.form, data=package)
    utils.populate_provider_choices(form.provider_id)

    if request.method == 'POST' and form.validate():
        try:
            package = api.put(f'/package/{id}', dict(
                provider_id=form.provider_id.data,
                title=(title := form.title.data),
            ))
            flash(f'Package <b>{title}</b> has been updated.', category='success')
            return redirect(url_for('.detail', id=id))

        except ODPAPIError as e:
            if response := api.handle_error(e):
                return response

    return render_template(
        'package_edit.html',
        package=package,
        form=form,
    )


@bp.route('/<id>/tag/doi', methods=('POST',))
@api.view(ODPScope.PACKAGE_DOI)
def tag_doi(id):
    form = DOITagForm(request.form)
    redirect_args = dict(id=id, _anchor='overview')

    if form.validate():
        try:
            api.post(f'/package/{id}/tag', dict(
                tag_id=ODPPackageTag.DOI,
                data={
                    'doi': form.doi.data,
                },
            ))
            flash(f'{ODPPackageTag.DOI} tag has been set.', category='success')
            return redirect(url_for('.detail', **redirect_args))

        except ODPAPIError as e:
            if response := api.handle_error(e):
                return response
    else:
        redirect_args |= dict(modal='tag-doi')

    return redirect(url_for('.detail', **redirect_args), code=307)


@bp.route('/<id>/tag/geoloc', methods=('POST',))
@api.view(ODPScope.PACKAGE_WRITE)
def tag_geolocation(id):
    form = GeoLocationTagForm(request.form)
    redirect_args = dict(id=id, _anchor='overview')

    if form.validate():
        try:
            tag_data = {
                'place': form.place.data,
                'shape': (shape := form.shape.data),
                'east': form.east.data,
                'north': form.north.data,
            }
            if shape == 'box':
                tag_data |= {
                    'west': form.west.data,
                    'south': form.south.data,
                }
            api.post(f'/package/{id}/tag', dict(
                tag_id=ODPPackageTag.GEOLOCATION,
                data=tag_data,
            ))
            flash(f'{ODPPackageTag.GEOLOCATION} tag has been set.', category='success')
            return redirect(url_for('.detail', **redirect_args))

        except ODPAPIError as e:
            if response := api.handle_error(e):
                return response
    else:
        redirect_args |= dict(modal='tag-geoloc')

    return redirect(url_for('.detail', **redirect_args), code=307)


@bp.route('/<id>/tag/daterange', methods=('POST',))
@api.view(ODPScope.PACKAGE_WRITE)
def tag_daterange(id):
    form = DateRangeTagForm(request.form)
    redirect_args = dict(id=id, _anchor='overview')

    if form.validate():
        try:
            api.post(f'/package/{id}/tag', dict(
                tag_id=ODPPackageTag.DATERANGE,
                data={
                    'start': form.start.data.isoformat(),
                    'end': form.end.data.isoformat(),
                },
            ))
            flash(f'{ODPPackageTag.DATERANGE} tag has been set.', category='success')
            return redirect(url_for('.detail', **redirect_args))

        except ODPAPIError as e:
            if response := api.handle_error(e):
                return response
    else:
        redirect_args |= dict(modal='tag-daterange')

    return redirect(url_for('.detail', **redirect_args), code=307)


@bp.route('/<id>/tag/contributor', methods=('POST',))
@api.view(ODPScope.PACKAGE_WRITE)
def tag_contributor(id):
    form = ContributorTagForm(request.form)
    utils.populate_keyword_choices(form.affiliations, ODPVocabulary.INSTITUTION, include_proposed=True)
    redirect_args = dict(id=id, _anchor='contributors')

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
            return redirect(url_for('.detail', **redirect_args))

        except ODPAPIError as e:
            if response := api.handle_error(e):
                return response
    else:
        redirect_args |= dict(modal='tag-contributor')

    return redirect(url_for('.detail', **redirect_args), code=307)


@bp.route('/<id>/add-institution', methods=('POST',))
@api.view(ODPScope.KEYWORD_SUGGEST)
def add_institution(id):
    """Add an unlisted institution (propose institution keyword)."""
    form = InstitutionKeywordForm(request.form)
    redirect_args = dict(id=id, _anchor='contributors')

    if form.validate():
        try:
            api_args = {'key': form.key.data, 'data': {}}
            if form.abbr.data:
                api_args['data']['abbr'] = form.abbr.data
            if form.ror.data:
                api_args['data']['ror'] = form.ror.data

            api.post('/keyword/Institution/', api_args)

        except ODPAPIError as e:
            if response := api.handle_error(e):
                return response
    else:
        redirect_args |= dict(modal='add-institution')

    return redirect(url_for('.detail', **redirect_args), code=307)


@bp.route('/<id>/upload-file', methods=('POST',))
@api.view(ODPScope.PACKAGE_WRITE)
def upload_file(id):
    """Add a file to a package and upload it to an archive."""
    form = FileUploadForm(request.form)
    redirect_args = dict(id=id, _anchor='resources')

    if form.validate():
        package = api.get(f'/package/{id}')
        provider_id = package['provider_id']
        archive_id = current_app.config['ARCHIVE_ID']
        file = request.files.get('file')
        filename = secure_filename(file.filename)
        try:
            api.put_files(
                f'/archive/{archive_id}/{provider_id}/{id}/',
                files={'file': file.stream},
                title=form.title.data or None,
                description=form.description.data or None,
                filename=filename,
                sha256=form.sha256.data,
                package_id=id,
            )
            flash(f'File <b>{filename}</b> has been uploaded.', category='success')
            return redirect(url_for('.detail', **redirect_args))

        except ODPAPIError as e:
            if response := api.handle_error(e):
                return response
    else:
        redirect_args |= dict(modal='upload-file')

    return redirect(url_for('.detail', **redirect_args), code=307)


@bp.route('/<id>/upload-zip', methods=('POST',))
@api.view(ODPScope.PACKAGE_WRITE)
def upload_zip(id):
    """Upload a zip file, unpacking its contents into the package."""
    form = ZipUploadForm(request.form)
    redirect_args = dict(id=id, _anchor='resources')

    if form.validate():
        package = api.get(f'/package/{id}')
        provider_id = package['provider_id']
        archive_id = current_app.config['ARCHIVE_ID']
        file = request.files.get('zip_file')
        filename = secure_filename(file.filename)
        try:
            api.put_files(
                f'/archive/{archive_id}/{provider_id}/{id}/',
                unpack=True,
                files={'file': file.stream},
                filename=filename,
                sha256=form.zip_sha256.data,
                package_id=id,
            )
            flash(f'Zip file <b>{filename}</b> has been uploaded and unpacked.', category='success')
            return redirect(url_for('.detail', **redirect_args))

        except ODPAPIError as e:
            if response := api.handle_error(e):
                return response
    else:
        redirect_args |= dict(modal='upload-zip')

    return redirect(url_for('.detail', **redirect_args), code=307)


@bp.route('/<id>/untag/doi/<tag_instance_id>', methods=('POST',))
@api.view(ODPScope.PACKAGE_DOI)
def untag_doi(id, tag_instance_id):
    return


@bp.route('/<id>/untag/geoloc/<tag_instance_id>', methods=('POST',))
@api.view(ODPScope.PACKAGE_WRITE)
def untag_geolocation(id, tag_instance_id):
    return


@bp.route('/<id>/untag/daterange/<tag_instance_id>', methods=('POST',))
@api.view(ODPScope.PACKAGE_WRITE)
def untag_daterange(id, tag_instance_id):
    return


@bp.route('/<id>/untag/contributor/<tag_instance_id>', methods=('POST',))
@api.view(ODPScope.PACKAGE_WRITE)
def untag_contributor(id, tag_instance_id):
    return


@bp.route('/<id>/resource/delete/<resource_id>', methods=('POST',))
@api.view(ODPScope.PACKAGE_WRITE)
def delete_resource(id, resource_id):
    return
