from datetime import datetime

import jwt
from tornado.auth import AuthError

from handlers.base import BaseHandler
from mixins import WexinOAuth2Mixin
from models.users import User
from settings import private_key


class WeixinOAuth2LoginHandler(BaseHandler, WexinOAuth2Mixin):
    """
    微信Oauth登录
    """
    async def post(self):
        ret = {}
        if self.get_json_argument('code', False):
            access = await self.get_authenticated_user(
                code=self.get_argument('code'))
            weixin_user = await self.oauth2_request(
                "https://api.weixin.qq.com/sns/userinfo",
                access_token=access["access_token"],
                openid=access['openid'],
                lang='zh_CN'
            )
            nickname, openid, gender, avatar = (weixin_user['nickname'],
                                                weixin_user['openid'],
                                                weixin_user['sex'],
                                                weixin_user['headimgurl'])
            try:
                user = await User.objects.get(User, openid=openid)
            except User.DoesNotExist:
                user = await User.objects.create(User,
                                                 nickname=nickname,
                                                 gender=gender,
                                                 openid=openid,
                                                 avatar=avatar)

            payload = {
                "id": user.id,
                "nickname": user.nickname,
                "exp": datetime.utcnow()
            }
            token = jwt.encode(payload, private_key, algorithm='RS256')
            if user.nickname is not None:
                ret["nickname"] = user.nickname
            else:
                ret["nickname"] = user.mobile
            ret["token"] = token.decode("utf8")

            self.finish(ret)
        else:
            raise AuthError("请携带code请求接口")
