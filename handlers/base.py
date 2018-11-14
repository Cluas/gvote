import json
import traceback

import tornado.web

import logging

from tornado.auth import AuthError

from exceptions import APIException
from mixins import TornadoCORSMixin

logger = logging.getLogger('vote.' + __name__)


class BaseHandler(TornadoCORSMixin, tornado.web.RequestHandler):
    """A class to collect common handler methods - all other handlers should
    subclass this one.
    """

    def data_received(self, chunk):
        pass

    def load_json(self):
        """Load JSON from the request body and store them in
        self.request.arguments, like Tornado does by default for POSTed form
        parameters.
        If JSON cannot be decoded, raises an HTTPError with status 400.
        """
        try:
            self.request.arguments = json.loads(self.request.body)
        except ValueError:
            msg = "Could not decode JSON: %s" % self.request.body
            logger.debug(msg)
            raise tornado.web.HTTPError(400, msg)

    def get_json_argument(self, name, default=None):
        """Find and return the argument with key 'name' from JSON request data.
        Similar to Tornado's get_argument() method.
        """
        if default is None:
            default = self._ARG_DEFAULT
        if not self.request.arguments and self.request.body:
            self.load_json()
        if name not in self.request.arguments:
            if default is self._ARG_DEFAULT:
                msg = "Missing argument '%s'" % name
                logger.debug(msg)
                raise tornado.web.HTTPError(400, msg)
            logger.debug("Returning default argument %s, as we couldn't find "
                         "'%s' in %s" % (default, name, self.request.arguments))
            return default
        arg = self.request.arguments[name]
        logger.debug("Found '%s': %s in JSON arguments" % (name, arg))
        return arg

    def write_error(self, status_code, **kwargs):
        """
        统一异常处理
        :param status_code:
        :param kwargs:
        :return:
        """
        if self.settings.get("serve_traceback") and "exc_info" in kwargs:
            # in debug mode, try to send a traceback
            self.set_header('Content-Type', 'text/plain')
            for line in traceback.format_exception(*kwargs["exc_info"]):
                self.write(line)
            self.finish()
        else:
            exc = kwargs["exc_info"][1]
            ret = {}
            if isinstance(exc, APIException):
                self.set_status(exc.status_code)
                ret.update(err_code=exc.code, err_msg=exc.detail)
                self.finish(ret)

            if isinstance(exc, AuthError):
                self.set_status(401)
