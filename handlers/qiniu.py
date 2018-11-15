from qiniu import Auth

from handlers.base import BaseHandler

import logging

logger = logging.getLogger('vote.' + __name__)


class QiNiuTokenHandler(BaseHandler):
    """
    七牛上传token生成接口
    """
    SUPPORTED_METHODS = ('GET', 'OPTIONS')

    async def get(self, *args, **kwargs):
        access_key = 'cN9wdCMb2ruONntEiXmBTXKXtAWKAKzpeOeU54xT'
        secret_key = '-0IUfDbSznGmoNl0bD-ewC5fKx3gR_kBlyorBB3B'
        q = Auth(access_key, secret_key)
        bucket_name = 'chair'
        token = q.upload_token(bucket_name)
        self.finish({'token': token})
