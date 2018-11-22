import hashlib
import json
import random
import string
import time

from tornado.httpclient import AsyncHTTPClient

from handlers.base import BaseHandler
from settings import APPID, SECRET_KEY, redis


class WeixinJSAPIHandler(BaseHandler):
    """
    微信Oauth登录
    """

    async def post(self, *args, **kwargs):
        param = self.request.body.decode("utf-8")
        data = json.loads(param)
        url = data.get('url')
        if not url:
            self.finish({'url': 'url是必填的'})
        jsapi_ticket = await self.get_jsapi_ticket()
        jsapi = self.jsapi(jsapi_ticket, url)
        self.finish(jsapi)

    async def get_access_token(self):
        access_token = redis.get('wexin_access_token')
        if not access_token:
            url = (f'https://api.weixin.qq.com/cgi-bin/token'
                   f'?grant_type=client_credential&appid={APPID}&secret={SECRET_KEY}')
            resp = await AsyncHTTPClient().fetch(url)
            content = resp.body.decode("utf-8")
            if "errcode" in content:
                self.finish(content)
            access_token = content['access_token']
            redis.set('wexin_access_token', access_token, 7100)
        return access_token

    async def get_jsapi_ticket(self):
        jsapi_ticket = redis.get('wexin_jsapi_ticket')
        if not jsapi_ticket:
            access_token = await self.get_access_token()
            url = (f'https://api.weixin.qq.com/cgi-bin/ticket/getticket'
                   f'?access_token={access_token}&type=jsapi')
            resp = await AsyncHTTPClient().fetch(url)
            content = resp.body.decode("utf-8")
            jsapi_ticket = content['ticket']
            redis.set('wexin_jsapi_ticket', access_token, 7100)
        return jsapi_ticket

    def sign(self, raw):
        raw = [(k, str(raw[k]) if isinstance(raw[k], int) else raw[k])
               for k in sorted(raw.keys())]
        s = "&".join("=".join(kv) for kv in raw if kv[1])
        return hashlib.sha1(s.encode("utf-8")).hexdigest()

    @property
    def nonce_str(self):
        char = string.ascii_letters + string.digits
        return "".join(random.choice(char) for _ in range(32))

    async def jsapi(self, ticket, url):
        timestamp = str(int(time.time()))
        nonce_str = self.nonce_str
        raw = dict(timestamp=timestamp,
                   noncestr=nonce_str, jsapi_ticket=ticket, url=url)
        sign = self.sign(raw)
        return raw.update(sign=sign)
