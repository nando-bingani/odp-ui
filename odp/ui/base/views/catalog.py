import json
from pathlib import Path
from random import randint
from typing import Optional

from flask import Blueprint, abort, current_app, make_response, redirect, render_template, request, url_for,Response,jsonify,send_file
from io import BytesIO
from datetime import datetime
import json

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer,Table, TableStyle
from reportlab.lib.units import inch

from odp.const import ODPMetadataSchema
from odp.lib.client import ODPAPIError
from odp.ui.base import api, cli
from odp.ui.base.forms import CatalogSearchForm

import requests


bp = Blueprint(
    'catalog', __name__,
    static_folder=Path(__file__).parent.parent / 'static',
)


@bp.app_template_filter()
def doi_title(doi: str) -> str:
    """Get the title for the given DOI."""
    if cached_title := cli.cache.get(doi, 'title'):
        return cached_title

    catalog_id = current_app.config['CATALOG_ID']
    try:
        if title := cli.get(
                f'/catalog/{catalog_id}/getvalue/{doi}',
                schema_id=ODPMetadataSchema.SAEON_DATACITE4,
                json_pointer='/titles/0/title',
        ):
            # titles rarely change, but we must expire them in case they ever do;
            # keep for between 7 and 14 days, so a large set of child record titles doesn't expire all at once
            cli.cache.set(doi, 'title', value=title, expiry=randint(604800, 1209600))

            return title

    except ODPAPIError:
        pass

    return ''


def _select_metadata(record: dict, schema_id: ODPMetadataSchema) -> Optional[dict]:
    return next(
        (metadata_record['metadata']
         for metadata_record in record['metadata_records']
         if metadata_record['schema_id'] == schema_id),
        None
    )


@bp.app_template_filter()
def select_datacite_metadata(record: dict) -> dict:
    """Select the DataCite metadata dict."""
    return _select_metadata(record, ODPMetadataSchema.SAEON_DATACITE4)


@bp.app_template_filter()
def select_iso19115_metadata(record: dict) -> Optional[dict]:
    """Select the ISO19115 metadata dict, if present."""
    return _select_metadata(record, ODPMetadataSchema.SAEON_ISO19115)


@bp.app_template_filter()
def select_schemaorg_metadata(record: dict) -> Optional[dict]:
    """Select the schema.org (JSON-LD) metadata dict, if present."""
    return _select_metadata(record, ODPMetadataSchema.SCHEMAORG_DATASET)


@bp.app_template_filter()
def select_ris_metadata(record: dict) -> Optional[dict]:
    """Select the RIS metadata dict, if present."""
    return _select_metadata(record, ODPMetadataSchema.RIS_CITATION)


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
    sort = request.args.get('sort', 'rank desc')
    page = request.args.get('page', 1)

    facet_api_query = {}
    facet_ui_query = {}
    facet_fields = {}
    for facet_title in facets:
        facet_field = CatalogSearchForm.facet_fieldname(facet_title)
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
        sort=sort,
        page=page,
        size=25,
    )

    return render_template(
        'catalog_index.html',
        form=CatalogSearchForm(request.args),
        result=result,
        facet_fields=facet_fields,
    )


@bp.route('/search', methods=('POST',))
def search():
    form = CatalogSearchForm(request.form)
    query = form.data
    query.pop('csrf_token')
    if not query['exclusive_region']:
        query.pop('exclusive_region')
    if not query['exclusive_interval']:
        query.pop('exclusive_interval')

    facets = current_app.config['CATALOG_FACETS']
    for facet_title in facets:
        if not query[facet_field := CatalogSearchForm.facet_fieldname(facet_title)]:
            query.pop(facet_field)

    return redirect(url_for( '.index', **query))


@bp.route('/<path:id>')
@cli.view()
@api.user()
def view(id):
    catalog_id = current_app.config['CATALOG_ID']

    record = cli.get(f'/catalog/{catalog_id}/records/{id}')

    return render_template(
        'catalog_record.html',
        record=record,
    )


@bp.route('/sitemap.xml')
@cli.view()
def sitemap():
    catalog_id = current_app.config['CATALOG_ID']

    catalog = cli.get(f'/catalog/{catalog_id}')
    try:
        sitemap_xml = catalog['data']['sitemap.xml']
    except (KeyError, TypeError):
        abort(404)

    response = make_response(sitemap_xml)
    response.headers['Content-Type'] = 'application/xml'
    return response


@bp.route('/subset')
@cli.view()
def subset_record_list():
    catalog_id = current_app.config['CATALOG_ID']
    record_ids = request.args.getlist('record_id_or_doi_list')
    record_ids_query = '&record_id_or_doi_list='.join(record_ids)
    # Prepend the first parameter
    record_ids_query = f"record_id_or_doi_list={record_ids_query}"
    # Pass the record IDs as query parameters

    #Add page and size on the query paramenters &page=1&size=50
    page = request.args.getlist('page')[0]

    size = request.args.getlist('size')[0]
    catalog_record_list = cli.get(f'/catalog/{catalog_id}/subset?{record_ids_query}&page={page}&size={size}')
    print("XXXXXXXXX",)
    print(json.dumps(catalog_record_list))
    print("sDS")
    return render_template(
        'catalog_subset.html',
        catalog_record_list=catalog_record_list,
    )

@bp.route('/proxy-download')
def proxy_download():
    url = request.args.get('url')
    print(url)
    r = requests.get(url)
    return Response(r.content, headers={
        'Content-Type': r.headers.get('Content-Type', 'application/octet-stream'),
        'Access-Control-Allow-Origin': '*'
    })

def build_metadata_pdf(data):
    """Return a BytesIO buffer containing a one‑page PDF that mimics the
    metadata table shown in the screenshots.
    """
    # ------------------------------------------------------------------
    # 1. -------- Extract pieces we need --------------------------------
    # ------------------------------------------------------------------
    record = data[0]
    meta   = record["metadata_records"][0]["metadata"]

    def _get_person(person):
        """Return (name, affiliation, email, orcid) for a creator / contributor"""
        name        = person.get("name", "N/A")
        affiliation = "N/A"
        email       = "N/A"
        orcid       = "N/A"

        for aff in person.get("affiliation", []):
            # Example format:  "Oceans and Coastal Research … , email: foo@bar"
            if "email:" in aff["affiliation"]:
                affiliation, email = map(str.strip, aff["affiliation"].split(", email:"))
            else:
                affiliation = aff["affiliation"]

        for idf in person.get("nameIdentifiers", []):
            if idf.get("nameIdentifierScheme") == "ORCID":
                orcid = idf["nameIdentifier"]

        return name, affiliation, email, orcid

    # High‑level fields
    title        = meta["titles"][0]["title"]
    doi          = meta["doi"]
    publisher    = meta["publisher"]
    pub_year     = meta["publicationYear"]
    keywords     = ", ".join(record["keywords"])

    abstract     = meta["descriptions"][0]["description"]
    t_start      = datetime.fromisoformat(record["temporal_start"]).strftime("%d %b %Y")
    t_end        = datetime.fromisoformat(record["temporal_end"]).strftime("%d %b %Y")

    geo_box      = meta["geoLocations"][0]["geoLocationBox"]
    geo_str      = (
        f"North: {geo_box['northBoundLatitude']}\n"
        f"South: {geo_box['southBoundLatitude']}\n"
        f"West: {geo_box['westBoundLongitude']}\n"
        f"East: {geo_box['eastBoundLongitude']}"
    )

    creator      = meta["creators"][0]
    contributor  = meta["contributors"][0]
    cr_name, cr_aff, cr_email, cr_orcid = _get_person(creator)
    c_name,  c_aff,  c_email,  c_orcid  = _get_person(contributor)

    licence      = meta["rightsList"][0]
    licence_txt  = (
        f'<link href="{licence["rightsURI"]}">{licence["rights"]}</link>'
    )

    # ------------------------------------------------------------------
    # 2. -------- Paragraph & table styles ------------------------------
    # ------------------------------------------------------------------
    styles           = getSampleStyleSheet()
    label_style      = ParagraphStyle(
        "label",
        parent=styles["BodyText"],
        fontSize=10,
        leading=13,
        spaceAfter=0,
        spaceBefore=2,
        leftIndent=0,
        rightIndent=6,
        textColor=colors.black,
        wordWrap="LTR",
        bold=True,
    )
    value_style      = ParagraphStyle(
        "value",
        parent=styles["BodyText"],
        fontSize=10,
        leading=13,
        spaceAfter=0,
        spaceBefore=2,
    )
    title_value_style = ParagraphStyle(
        "title_value",
        parent=value_style,
        fontSize=11,
        leading=14,
        spaceBefore=0,
        spaceAfter=2,
        bold=True,
    )

    # ------------------------------------------------------------------
    # 3. -------- Build the table rows ----------------------------------
    # ------------------------------------------------------------------
    rows = [
        [Paragraph("Title",   label_style),
         Paragraph(title,     title_value_style)],


        [Paragraph("DOI", label_style),
         Paragraph(f'<link href="https://doi.org/{doi}">https://doi.org/{doi}</link>', value_style)],

        [Paragraph("Authors", label_style),
         Paragraph(f"{cr_name}<br/>{cr_aff}, email: {cr_email}", value_style)],

        [Paragraph("Publisher", label_style),
         Paragraph(f"{publisher} ({pub_year})", value_style)],

        [Paragraph("Contributors", label_style),
         Paragraph(
             f"Contact Person: {c_name}<br/>{c_aff},<br/>email: {c_email}",
             value_style,
         )],

        [Paragraph("Abstract", label_style),
         Paragraph(abstract, value_style)],

        [Paragraph("Data", label_style),
         Paragraph(licence_txt, value_style)],

        [Paragraph("Temporal extent", label_style),
         Paragraph(f"{t_start} – {t_end}", value_style)],

        [Paragraph("Geographic extent", label_style),
         Paragraph(geo_str.replace("\n", "<br/>"), value_style)],

        [Paragraph("Keywords", label_style),
         Paragraph(keywords, value_style)],
    ]

    # ------------------------------------------------------------------
    # 4. -------- Assemble the table & PDF ------------------------------
    # ------------------------------------------------------------------
    table = Table(
        rows,
        colWidths=[1.6 * inch, 5.3 * inch],  # narrow label / wide value
        hAlign="LEFT",
        repeatRows=0,
    )

    # Grey horizontal rule beneath every row
    tbl_style = [
        ("VALIGN",    (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING",(0, 0), (-1, -1), 2),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 4),
        ("LINEBELOW", (0, 0), (-1, 0), 0.25, colors.lightgrey),
    ]
    # add LINEBELOW for every subsequent row
    for r in range(1, len(rows)):
        tbl_style.append(("LINEBELOW", (0, r), (-1, r), 0.25, colors.lightgrey))

    table.setStyle(TableStyle(tbl_style))

    # Build the document
    buffer = BytesIO()
    doc    = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    story = [table, Spacer(1, 0.2 * inch)]
    doc.build(story)
    buffer.seek(0)
    return buffer

@bp.route('/format/metadata.pdf', methods=['POST'])
def format_metadata_pdf():
    metadata = request.get_json()
    if not metadata:
        return jsonify({"error": "No metadata provided"}), 400

    try:
        pdf_buffer = build_metadata_pdf(metadata)
        pdf_buffer.seek(0)
        return send_file(pdf_buffer, mimetype='application/pdf', as_attachment=True, download_name='metadata.pdf')
    except Exception as e:
        return jsonify({"error": str(e)}), 500
