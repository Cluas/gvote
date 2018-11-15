import json
import logging

from exceptions import NotFoundError
from forms.gifts import GiftSendForm
from handlers.base import BaseHandler
from models import objects
from models.gifts import Gift
from models.votes import Candidate
from settings import redis
from utils.decorators import async_authenticated
from utils.async_weixin import async_weixin_pay

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

        gifts = await objects.execute(query)
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


class GiftSendHandler(BaseHandler):
    SUPPORTED_METHODS = ('POST', 'OPTIONS')

    @async_authenticated
    async def post(self, candidate_id, *args, **kwargs):
        param = self.request.body.decode("utf-8")
        data = json.loads(param)
        gift_send_form = GiftSendForm.from_json(data)
        if gift_send_form.validate():
            user = self.current_user
            gift_id = gift_send_form.gift_id.data
            num = gift_send_form.num.data

            async with objects.database.atomic_async():
                try:
                    gift = await objects.get(Gift, id=candidate_id)
                    candidate = await objects.get(Candidate, id=candidate_id)

                    out_trade_no = async_weixin_pay.out_trade_no
                    ret = await async_weixin_pay.jsapi(
                        openid=user.openid,
                        body=gift.name,
                        out_trade_no=out_trade_no,
                        total_fee=int(gift.price * num * 100),
                    )

                    print(ret)

                    redis.hmset(out_trade_no, {'gift_id': f'{gift_id}',
                                               'candidate_id': f'{candidate_id}',
                                               'amount': f'{gift.price * num}',
                                               'num': f'{num}',
                                               'vote_id': f'{candidate.vote_id}'},
                                )
                    redis.expire(out_trade_no, 15 * 60)
                    print(out_trade_no)

                    self.finish(ret)
                except Gift.DoesNotExist:
                    raise NotFoundError("礼物不存在")
                except Candidate.DoesNotExist:
                    raise NotFoundError("选手不存在")
