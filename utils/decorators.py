import functools
import jwt

from exceptions import AuthenticationFailed
from models.users import User


def async_authenticated(func):
    @functools.wraps(func)
    async def wrapper(self, *args, **kwargs):
        token = self.request.headers.get("Authorization", b'').split()
        if isinstance(token, str):
            # Work around django test client oddness
            token = token.encode('iso-8859-1')

        if token:
            try:
                token = token[1]
                payload = jwt.decode(token, self.settings["secret_key"], leeway=self.settings["jwt_expire"],
                                     options={"verify_exp": True})
                user_id = payload["id"]

                # 从数据库中获取到user并设置给_current_user
                try:
                    user = await self.application.objects.get(User.select(User).where(User.id == user_id))
                    self._current_user = user

                    # 此处很关键
                    await func(self, *args, **kwargs)
                except User.DoesNotExist:
                    self.set_status(401)
            except jwt.ExpiredSignatureError:
                self.set_status(401)
        else:
            self.set_status(401)
            self.finish(
                dict(
                    err_code='authentication_failed', err_msg='认证失败'
                )
            )

    return wrapper
