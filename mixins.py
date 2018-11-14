import functools

from tornado import escape
from tornado.auth import OAuth2Mixin, _auth_return_future, AuthError
from tornado.concurrent import future_set_result_unless_cancelled
from tornado.stack_context import wrap

from tools.pagination import Pagination

try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse

try:
    import urllib.parse as urllib_parse
except ImportError:
    import urllib as urllib_parse


class TornadoCORSMixin:
    """
    跨域支持mixin
    """

    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Headers', '*')
        self.set_header('Access-Control-Max-Age', 1000)
        self.set_header('Content-type', 'application/json')
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, DELETE, PUT, PATCH, OPTIONS')
        self.set_header('Access-Control-Allow-Headers',
                        'Content-Type, '
                        'Authorization, '
                        'Access-Control-Allow-Origin,'
                        'Access-Control-Allow-Headers, '
                        'X-Requested-By, '
                        'Access-Control-Allow-Methods')

    def options(self, *args, **kwargs):
        pass


class WexinOAuth2Mixin(OAuth2Mixin):
    """
    WeChat authentication using OAuth2.
    """
    _OAUTH_AUTHORIZE_URL = 'https://open.weixin.qq.com/connect/qrconnect'
    _OAUTH_ACCESS_TOKEN_URL = 'https://api.weixin.qq.com/sns/oauth2/access_token'
    _OAUTH_USERINFO_URL = 'https://api.weixin.qq.com/sns/userinfo'
    _OAUTH_NO_CALLBACKS = False
    _OAUTH_SETTINGS_KEY = 'wexin_oauth'

    @_auth_return_future
    def get_authenticated_user(self, code, callback):
        """
        Handles the login for the Wexin user, returning an access token.
        """
        http = self.get_auth_http_client()
        body = urllib_parse.urlencode({
            "code": code,
            "appid": self.settings[self._OAUTH_SETTINGS_KEY]['key'],
            "secret": self.settings[self._OAUTH_SETTINGS_KEY]['secret'],
            "grant_type": "authorization_code",
        })

        fut = http.fetch(self._OAUTH_ACCESS_TOKEN_URL,
                         method="POST",
                         headers={'Content-Type': 'application/x-www-form-urlencoded'},
                         body=body)
        fut.add_done_callback(wrap(functools.partial(self._on_access_token, callback)))

    def _on_access_token(self, future, response_fut):
        """Callback function for the exchange to the access token."""
        try:
            response = response_fut.result()
        except Exception as e:
            future.set_exception(AuthError('Wexin auth error: %s' % str(e)))
            return

        args = escape.json_decode(response.body)
        if args.get('errcode'):
            future.set_exception(AuthError('Wexin auth error: %s' % str(args['errmsg'])))
            return
        future_set_result_unless_cancelled(future, args)


class PaginationMixin:
    pagination_class = Pagination

    def get_paginate_query(self, query):

        query = self.paginator.paginate_queryset(query, self)
        return query

    def get_paginated_response(self, data):
        """
        Return a paginated style `Response` object for the given output data.
        """
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)

    @property
    def paginator(self):
        """
        The paginator instance associated with the view, or `None`.
        """
        if not hasattr(self, '_paginator'):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        return self._paginator
