#!/usr/bin/env python
import os
import sys

import tornado.ioloop
import tornado.web
import wtforms_json
from peewee_async import Manager
from tornado.options import define, options

from settings import database, settings


def make_app(debug=False):
    from urls import urlpatterns
    return tornado.web.Application(urlpatterns, debug=debug, **settings)


define("port", default=9090, help="server listen port")
define("settings", default="develop", help="server settings file")


def serve():
    wtforms_json.init()
    # init_log()

    app = make_app(False)

    app.listen(options.port)

    # No need for sync anymore!
    objects = Manager(database)
    database.set_allow_sync(False)
    app.objects = objects

    sys.stdout.write(f"Start server at:http://0.0.0.0:{options.port} \nSettings: {options.settings}\n")
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    current_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, current_path)
    serve()
