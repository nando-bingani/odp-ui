import json
import secrets
from dataclasses import asdict, dataclass
from typing import Optional

import requests
from authlib.integrations.flask_client import OAuth
from flask import Flask, redirect, request, url_for
from flask_login import LoginManager, current_user, login_user, logout_user
from redis import Redis

from odp.client import ODPBaseClient


@dataclass
class LocalUser:
    """Represents a client-side, logged-in user. Compatible with Flask-Login."""

    id: str
    name: str
    email: str
    active: bool
    verified: bool
    picture: Optional[str]
    role_ids: list[str]

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @property
    def is_active(self):
        return self.active and self.verified

    def get_id(self):
        return self.id


class ODPUIClient(ODPBaseClient):
    """ODP client for a Flask app, providing signup, login and logout routes,
    and API access with a logged in user's access token."""

    def __init__(
            self,
            api_url: str,
            hydra_url: str,
            client_id: str,
            client_secret: str,
            scope: list[str],
            cache: Redis,
            app: Flask,
    ) -> None:
        super().__init__(api_url, hydra_url, client_id, client_secret, scope)
        self.cache = cache
        self.oauth = OAuth(
            app=app,
            cache=cache,
            fetch_token=self._fetch_token,
            update_token=self._update_token,
        )
        self.oauth.register(
            name='hydra',
            client_id=client_id,
            client_secret=client_secret,
            client_kwargs={'scope': ' '.join(scope)},
            server_metadata_url=f'{hydra_url}/.well-known/openid-configuration',
        )

        app.add_url_rule('/oauth2/signup', endpoint='hydra.signup', view_func=self._signup)
        app.add_url_rule('/oauth2/login', endpoint='hydra.login', view_func=self._login)
        app.add_url_rule('/oauth2/logout', endpoint='hydra.logout', view_func=self._logout)
        app.add_url_rule('/oauth2/logged_in', endpoint='hydra.logged_in', view_func=self._logged_in)
        app.add_url_rule('/oauth2/logged_out', endpoint='hydra.logged_out', view_func=self._logged_out)

        login_manager = LoginManager(app)

        @login_manager.user_loader
        def load_user(user_id):
            return self._get_user(user_id)

    def _send_request(self, method: str, url: str, data: dict, params: dict) -> requests.Response:
        """Send a request to the API with the user's access token."""
        return self.oauth.hydra.request(method, url, json=data, params=params)

    def _signup(self):
        """Initiate signup.

        Return a redirect to the Hydra authorization endpoint.
        """
        redirect_uri = url_for('hydra.logged_in', _external=True)
        return self.oauth.hydra.authorize_redirect(redirect_uri, mode='signup')

    def _login(self):
        """Initiate login.

        Return a redirect to the Hydra authorization endpoint.
        """
        redirect_uri = url_for('hydra.logged_in', _external=True)
        return self.oauth.hydra.authorize_redirect(redirect_uri, mode='login')

    def _logged_in(self):
        """Callback from Hydra after a successful login via the identity service.

        Fetch and cache the token, user info and permissions, and log the user
        in to the app.
        """
        token = self.oauth.hydra.authorize_access_token()
        userinfo = token.pop('userinfo')

        localuser = LocalUser(
            id=(user_id := userinfo['sub']),
            name=userinfo['name'],
            email=userinfo['email'],
            verified=userinfo['email_verified'],
            picture=userinfo['picture'],
            role_ids=userinfo['roles'],
            active=True,  # we'll only get to this point if the user is active
        )

        token_data = self.get('/token/')
        user_permissions = token_data['permissions']

        self.cache.hset(self._cache_key(user_id, 'token'), mapping=token)
        self.cache.set(self._cache_key(user_id, 'user'), json.dumps(asdict(localuser)))
        self.cache.set(self._cache_key(user_id, 'permissions'), json.dumps(user_permissions))

        login_user(localuser)

        return redirect(url_for('home.index'))

    def _logout(self):
        """Initiate logout.

        Return a redirect to the Hydra endsession endpoint.
        """
        redirect_uri = url_for('hydra.logged_out', _external=True)

        if user_id := current_user.get_id():
            token = self.oauth.fetch_token('hydra')
            state_val = secrets.token_urlsafe()
            self.cache.set(self._cache_key(user_id, 'state'), state_val, ex=10)
            url = f'{self.hydra_url}/oauth2/sessions/logout' \
                  f'?id_token_hint={token.get("id_token")}' \
                  f'&post_logout_redirect_uri={redirect_uri}' \
                  f'&state={state_val}'

            return redirect(url)

        return redirect(url_for('home.index'))

    def _logged_out(self):
        """Callback from Hydra after logging out via the identity service.

        Log the user out of the app.
        """
        if user_id := current_user.get_id():
            state_val = request.args.get('state')
            if state_val == self.cache.get(key := self._cache_key(user_id, 'state')):
                logout_user()
                self.cache.delete(key)

        return redirect(url_for('home.index'))

    def _get_user(self, user_id):
        """Return the cached user object."""
        if serialized_user := self.cache.get(self._cache_key(user_id, 'user')):
            return LocalUser(**json.loads(serialized_user))

    def get_permissions(self, user_id):
        """Return the cached user permissions."""
        if serialized_permissions := self.cache.get(self._cache_key(user_id, 'permissions')):
            return json.loads(serialized_permissions)

    def _cache_key(self, user_id, key):
        return f'{self.__class__.__name__}.{self.client_id}.{user_id}.{key}'

    def _fetch_token(self, hydra):
        if user_id := current_user.get_id():
            return self.cache.hgetall(self._cache_key(user_id, 'token'))

    def _update_token(self, hydra, token, refresh_token=None, access_token=None):
        if user_id := current_user.get_id():
            self.cache.hset(self._cache_key(user_id, 'token'), mapping=token)
