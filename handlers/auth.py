import json
from datetime import datetime

import jwt

from forms.jwt import JWTTokenForm
from forms.users import SmsCodeForm
from handlers.base import BaseHandler
from models.users import User
from settings import redis
from utils.async_yunpian import yunpian, generate_code


class JWTTokenHandler(BaseHandler):
    async def post(self, *args, **kwargs):
        ret = {}

        param = self.request.body.decode("utf-8")
        param = json.loads(param)
        form = JWTTokenForm.from_json(param)

        if form.validate():
            mobile = form.mobile.data
            password = form.password.data

            try:
                user = await self.application.objects.get(User, mobile=mobile)
                if not user.password.check_password(password):
                    self.set_status(400)
                    ret["non_fields"] = "用户名或密码错误"
                else:
                    payload = {
                        "id": user.id,
                        "nickname": user.nickname,
                        "exp": datetime.utcnow()
                    }
                    token = jwt.encode(payload, self.settings["secret_key"], algorithm='HS256')
                    ret["id"] = user.id
                    if user.nick_name is not None:
                        ret["nickname"] = user.nickname
                    else:
                        ret["nickname"] = user.mobile
                        ret["token"] = token.decode("utf8")

            except User.DoesNotExist as e:
                self.set_status(400)
                ret["mobile"] = "用户不存在"

            self.finish(ret)


class SmsHandler(BaseHandler):
    """
    短信接口
    """

    async def post(self, *args, **kwargs):

        ret = {}

        param = self.request.body.decode("utf-8")
        param = json.loads(param)
        sms_form = SmsCodeForm.from_json(param)
        if sms_form.validate():
            mobile = sms_form.mobile.data
            code = generate_code()

            re_json = await yunpian.send_single_sms(code, mobile)
            if re_json["code"] != 0:
                self.set_status(400)
                ret["mobile"] = re_json["msg"]
            else:
                redis.set(f"{mobile}_{code}", 1, 10 * 60)
        else:
            self.set_status(400)
            for field in sms_form.errors:
                ret[field] = sms_form.errors[field][0]

        self.finish(ret)
