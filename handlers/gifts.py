import json
import logging

from handlers.base import BaseHandler
from models.gifts import Gift

logger = logging.getLogger('vote.' + __name__)


class GiftListHandler(BaseHandler):
    """
    礼物列表接口
    """
    SUPPORTED_METHODS = ('GET', 'OPTIONS')

    async def get(self, *args, **kwargs):
        query = Gift.select(
            Gift.name,
            Gift.image,
            Gift.price,
            Gift.reach,
            Gift.id
        )

        gifts = await Gift.objects.execute(query)
        ret = []
        for gift in gifts:
            ret.append({
                'name': gift.name,
                'image': gift.image,
                'price': gift.price,
                'reach': gift.reach,
                'id': gift.id,
            })

        self.finish(json.dumps(ret))
