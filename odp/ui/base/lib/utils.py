from markupsafe import Markup

from odp.ui.base import api


def pagify(item_list: list) -> dict:
    """Convert a flat object list to a page result."""
    return {
        'items': item_list,
        'total': len(item_list),
        'page': 1,
        'pages': 1,
    }


def populate_collection_choices(field, include_none=False):
    collections = api.get('/collection/', sort='key', size=0)['items']
    field.choices = [('', '(None)')] if include_none else []
    field.choices += [
        (collection['id'], Markup(f"{collection['key']} &mdash; {collection['name']}"))
        for collection in collections
    ]


def populate_provider_choices(field, include_none=False):
    providers = api.get('/provider/', sort='key', size=0)['items']
    field.choices = [('', '(None)')] if include_none else []
    field.choices += [
        (provider['id'], Markup(f"{provider['key']} &mdash; {provider['name']}"))
        for provider in providers
    ]


def populate_metadata_schema_choices(field):
    schemas = api.get('/schema/', schema_type='metadata', size=0)['items']
    field.choices = [
        (schema['id'], schema['id'])
        for schema in schemas
        if schema['id'].startswith('SAEON')
    ]


def populate_scope_choices(field, scope_types=None):
    scopes = api.get('/scope/', size=0)['items']
    field.choices = [
        (scope['id'], scope['id'])
        for scope in scopes
        if scope_types is None or scope['type'] in scope_types
    ]


def populate_role_choices(field, include_none=False):
    roles = api.get('/role/', size=0)['items']
    field.choices = [('', '(None)')] if include_none else []
    field.choices += [
        (role['id'], role['id'])
        for role in roles
    ]


def populate_keyword_choices(field, vocabulary_id, include_none=False):
    vocabulary = api.get(f'/vocabulary/{vocabulary_id}', size=0)
    field.choices = [('', '(None)')] if include_none else []
    field.choices += [
        (term['id'], term['id'])
        for term in vocabulary['terms']
    ]


def populate_sdg_choices(field, vocabulary_id, include_none=False):
    vocabulary = api.get(f'/vocabulary/{vocabulary_id}', size=0)
    field.choices = [('', '(None)')] if include_none else []
    field.choices += [
        (term['id'], f"{term['id']} - {term['data']['title']}")
        for term in vocabulary['terms']
    ]
