from flask import session
from wtforms import Form
from wtforms.csrf.session import SessionCSRF


class BaseForm(Form):
    class Meta:
        csrf = True
        csrf_class = SessionCSRF

        @property
        def csrf_context(self):
            return session
