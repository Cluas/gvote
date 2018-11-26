import os

import peewee_async
import redis

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPID = 'wx45973a96444c3cf2'
SECRET_KEY = '3efebe11ba2097f52ea27a2f5f5e4752'
settings = {
    "static_path": BASE_DIR + "/static",
    "static_url_prefix": "/static/",
    "template_path": "templates",
    "secret_key": "ZGGA#Mp4yL4w5CDu",
    "jwt_expire": 7 * 24 * 3600,
    "MEDIA_ROOT": os.path.join(BASE_DIR, "media"),
    "SITE_URL": "http://127.0.0.1:8888",
    "database": {
        "host": "127.0.0.1",
        "user": "root",
        "password": "root",
        "name": "message",
        "port": 3306
    },
    "redis": {
        "host": "127.0.0.1",
        'decode_responses': True
    },
    'wexin_oauth': {
        'key': APPID,
        'secret': SECRET_KEY
    }
}

database = peewee_async.MySQLDatabase(
    'vote', host="127.0.0.1", port=3306, user="root", password="imyuols123"
)

redis = redis.StrictRedis(**settings["redis"])

private_key = open(BASE_DIR + '/jwt-key').read()

public_key = open(BASE_DIR + '/jwt-key.pub').read()
