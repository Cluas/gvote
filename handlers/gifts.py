import json
import logging

from exceptions import NotFoundError
from forms.gifts import GiftSendForm
from handlers.base import BaseHandler
from models import objects
from models.gifts import Gift
from models.votes import Candidate, VoteEvent
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

                    redis.hmset(out_trade_no, {'gift_id': f'{gift_id}',
                                               'candidate_id': f'{candidate_id}',
                                               'amount': f'{gift.price * num}',
                                               'number_of_gifts': f'{num}',
                                               'voter_id': f'{user.id}',
                                               'voter_nickname': f'{user.nickname}',
                                               'voter_avatar': f'{user.avatar}',
                                               'image': f'{gift.image}',
                                               'reach': f'{gift.reach*num}',
                                               'vote_id': f'{candidate.vote_id}'},
                                )
                    redis.expire(out_trade_no, 10 * 60)
                    print(out_trade_no)

                    self.finish(ret)
                except Gift.DoesNotExist:
                    raise NotFoundError("礼物不存在")
                except Candidate.DoesNotExist:
                    raise NotFoundError("选手不存在")


class WeixinNotifyHandler(BaseHandler):

    async def post(self, *args, **kwargs):
        content = self.request.body.decode("utf-8")
        data = async_weixin_pay.to_dict(content)
        self.set_header('Content-Type', 'application/xml')
        if not async_weixin_pay.check(data):
            self.finish(async_weixin_pay.reply("签名验证失败", False))
        result_code = data['result_code']
        if result_code == 'SUCCESS':
            out_trade_no = data['out_trade_no']
            gift_data = redis.hgetall(out_trade_no)
            if gift_data:
                async with objects.database.atomic_async():
                    vote_event = await objects.create(VoteEvent,
                                                      gift_id=gift_data['gift_id'],
                                                      candidate_id=gift_data['candidate_id'],
                                                      amount=gift_data['amount'],
                                                      number_of_gifts=gift_data['number_of_gifts'],
                                                      voter_id=gift_data['voter_id'],
                                                      voter_nickname=gift_data['voter_nickname'],
                                                      voter_avatar=gift_data['voter_avatar'],
                                                      vote_id=gift_data['vote_id'],
                                                      reach=gift_data['reach'],
                                                      image=gift_data['image'],
                                                      out_trade_no=out_trade_no)

                    candidate = await objects.get(Candidate, id=vote_event.candidate_id)
                    candidate.number_of_votes += vote_event.reach
                    await objects.update(candidate)
                    redis.delete(out_trade_no)
                    self.finish(async_weixin_pay.reply('OK', True))

            self.finish(async_weixin_pay.reply('OK', True))
