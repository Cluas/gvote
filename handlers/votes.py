import json
import logging
from datetime import date

from playhouse.shortcuts import model_to_dict

from exceptions import NotFoundError, IsVoteError, ErrorCode, DuplicateError, DisableVoting
from forms.votes import CandidateForm, VoteEventForm, VoteForm, VoteUpdateForm, CandidateStatusForm
from handlers.base import BaseHandler, GenericHandler
from mixins import ListModelMixin
from models import objects
from models.users import User
from models.votes import Candidate, Vote, VoteEvent, VoteBanner, CandidateImage
from settings import redis
from utils.decorators import async_authenticated, async_admin_required
from utils.json import json_serializer

logger = logging.getLogger('vote.' + __name__)


class VoteDetailHandler(BaseHandler):
    """
    投票详情接口
    """

    async def get(self, pk, *args, **kwargs):
        try:
            await objects.get(Vote, id=pk)
            query = Vote.get_vote_info_by_pk(pk)

            vote = await objects.prefetch(query, VoteBanner.select())

            vote = vote[0]
            vote.views += 1
            await objects.update(vote)

            banners = [banner.image for banner in vote.banners]
            ret = dict(
                banners=banners,
                start_time=vote.start_time,
                end_time=vote.end_time,
                views=vote.views,
                announcement=vote.announcement,
                title=vote.title,
                description=vote.description,
                number_of_votes=int(vote.number_of_votes),
                number_of_candidates=vote.number_of_candidates,
            )
            self.finish(json.dumps(ret, default=json_serializer))
        except Vote.DoesNotExist:
            raise NotFoundError("投票活动不存在")

    async def put(self, pk, *args, **kwargs):
        try:
            vote = await objects.get(Vote, id=pk)
            param = self.request.body.decode("utf-8")
            data = json.loads(param)
            form = VoteUpdateForm.from_json(data)
            if form.validate():
                banners = form.data.pop('banners', [])
                form.data.cover = banners[0]
                for key, value in form.data.items():
                    setattr(vote, key, value)
                if banners:
                    await objects.delete(VoteBanner.select().where(VoteBanner.vote == vote))
                    for banner in banners:
                        await objects.create(VoteBanner, vote_id=vote.id, image=banner)
                self.finish(json.dumps(model_to_dict(Vote), default=json_serializer))

            else:
                ret = {}
                self.set_status(400)
                for field in form.errors:
                    ret[field] = form.errors[field][0]
                self.finish(ret)

        except Vote.DoesNotExist:
            raise NotFoundError("投票活动不存在")


class CandidateListHandler(ListModelMixin, GenericHandler):
    """
    选手列表接口
    """

    SUPPORTED_METHODS = ('GET', 'POST', 'OPTIONS')

    def get_query(self):
        vote_id = self.path_args[0]
        query = Candidate.query_candidates_by_vote_id(vote_id=vote_id)
        return query

    def filter_query(self, query):
        ordering = self.get_argument("ordering", None)
        key = self.get_argument("key", None)
        if ordering == '1':
            query = query.order_by(Candidate.create_time.desc())
        elif ordering == '0':
            query = query.order_by(Candidate.number_of_votes.desc())
        if key:
            query = query.where(User.name.contains(key) | Candidate.number.contains(key))
        return query

    @staticmethod
    def get_serializer_data(candidates):
        ret = []
        for candidate in candidates:
            ret.append(dict(
                cover=candidate.cover,
                id=candidate.id,
                name=candidate.user.name,
                number=candidate.number,
                number_of_votes=candidate.number_of_votes,
                diff=candidate.diff,
                vote_rank=candidate.vote_rank))
        return ret

    @async_authenticated
    async def post(self, vote_id, *args, **kwargs):

        param = self.request.body.decode("utf-8")
        data = json.loads(param)

        candidate_form = CandidateForm.from_json(data)
        if candidate_form.validate():

            user = self.current_user
            is_new = True if not user.mobile else False
            declaration = candidate_form.declaration.data
            images = candidate_form.images.data

            async with objects.database.atomic_async():

                try:
                    await objects.get(Vote, id=vote_id)
                    if is_new:
                        mobile = candidate_form.mobile.data
                        code = candidate_form.code.data
                        redis_key = "{}_{}".format(mobile, code)
                        if not redis.get(redis_key):
                            raise ErrorCode
                        user.mobile = mobile
                        user.name = candidate_form.name.data
                        await objects.update(user)
                    candidate = await objects.get(Candidate, user=user, vote_id=vote_id)

                    if not candidate.is_active:
                        raise DisableVoting("您已被禁止参加此次投票！")
                    raise DuplicateError

                except Candidate.DoesNotExist:

                    count = await objects.count(Candidate.select().where(Candidate.vote_id == vote_id))
                    number = "%03d" % (count + 1)
                    candidate = await objects.create(Candidate,
                                                     vote_id=vote_id,
                                                     declaration=declaration,
                                                     cover=images[0],
                                                     number=number,
                                                     user=user)
                    for image in images:
                        await objects.create(CandidateImage, candidate=candidate, url=image)

                    self.finish({"candidate_id": candidate.id})

                except Vote.DoesNotExist:

                    raise NotFoundError("投票不存在")


class CandidateDetailHandler(BaseHandler):
    """
    选手详情接口
    """
    SUPPORTED_METHODS = ('GET', 'OPTIONS')

    async def get(self, vote_id, candidate_id, *args, **kwargs):
        try:

            await objects.get(Vote, id=vote_id)

            query = Candidate.query_candidates_by_vote_id(vote_id=vote_id).where(Candidate.id == candidate_id)
            candidate = await objects.prefetch(query, CandidateImage.select())
            candidate = candidate[0]

            ret = dict(
                name=candidate.user.name,
                number=candidate.number,
                images=[image.url for image in candidate.images],
                declaration=candidate.declaration,
                number_of_votes=candidate.number_of_votes,
                diff=candidate.diff,
                rank=candidate.vote_rank)

            self.finish(json.dumps(ret))

        except IndexError:
            raise NotFoundError("选手不存在")
        except Vote.DoesNotExist:
            raise NotFoundError("投票不存在")


class VoteEventDetailHandler(ListModelMixin, GenericHandler):
    """
    投票事件流列表接口
    """
    SUPPORTED_METHODS = ('GET', 'OPTIONS')

    async def get(self, candidate_id, *args, **kwargs):

        try:
            await objects.get(Candidate, id=candidate_id)

            await super().get(candidate_id, *args, **kwargs)

        except Candidate.DoesNotExist:
            raise NotFoundError("参赛选手未找到")

    def get_query(self):
        candidate_id = self.path_args[0]
        query = VoteEvent.select().where(VoteEvent.candidate_id == candidate_id).order_by(VoteEvent.create_time.desc())
        return query

    @staticmethod
    def get_serializer_data(vote_events):
        ret = []
        for vote_event in vote_events:
            ret.append(dict(
                voter_avatar=vote_event.voter_avatar,
                voter_nickname=vote_event.voter_nickname,
                reach=vote_event.reach,
                image=vote_event.image,
                is_gift=vote_event.is_gift,
                number_of_gifts=vote_event.number_of_gifts,
                create_time=vote_event.create_time))
        return ret


class VoteRankListHandler(BaseHandler):
    """
    投票贡献排行
    """
    SUPPORTED_METHODS = ('GET', 'OPTIONS')

    async def get(self, candidate_id, *args, **kwargs):
        try:
            await objects.get(Candidate, id=candidate_id)
            query = VoteEvent.get_vote_rank(candidate_id)
            ranks = await objects.execute(query)

            ret = []
            for rank in ranks:
                ret.append(dict(
                    voter_avatar=rank.voter_avatar,
                    voter_nickname=rank.voter_nickname,
                    number_of_votes=int(rank.number_of_votes),
                    vote_rank=rank.vote_rank
                ))
            self.finish(json.dumps(ret))
        except Candidate.DoesNotExist:
            raise NotFoundError("参赛选手未找到")


class VoteRoleHandler(BaseHandler):
    """
    投票规则
    """
    SUPPORTED_METHODS = ('GET', 'OPTIONS')

    async def get(self, pk, *args, **kwargs):
        try:
            vote = await objects.get(Vote, id=pk)

            self.finish({'detail': vote.rules})
        except Vote.DoesNotExist:
            raise NotFoundError("投票未找到")


class VotingHandler(BaseHandler):
    """
    投票接口
    """
    SUPPORTED_METHODS = ('POST', 'OPTIONS')

    @async_authenticated
    async def post(self, candidate_id, *args, **kwargs):

        try:
            if not self.current_user.can_vote:
                raise DisableVoting
            async with objects.database.atomic_async():
                candidate = await objects.get(Candidate, id=candidate_id)
                if self.current_user.id == candidate.user_id:
                    raise DisableVoting("不能给自己投票")
                key = f'vote_user_{self.current_user.id}_date_{date.today()}'
                is_vote = redis.get(key)
                if is_vote:
                    raise IsVoteError
                await objects.create(VoteEvent,
                                     vote_id=candidate.vote_id,
                                     voter_id=self.current_user.id,
                                     voter_avatar=self.current_user.avatar,
                                     voter_nickname=self.current_user.nickname,
                                     candidate_id=candidate.id,
                                     reach=1)
                candidate.number_of_votes += 1
                await objects.update(candidate)
                redis.set(key, '1', 24 * 60 * 60)
            self.finish(json.dumps({'number_of_votes': candidate.number_of_votes}))
        except Candidate.DoesNotExist:
            raise NotFoundError("参赛选手未找到")


class VoteEventListHandler(ListModelMixin, GenericHandler):
    """
    投票事件流列表接口
    """
    query = VoteEvent.admin_extend()
    SUPPORTED_METHODS = ('GET', 'OPTIONS')

    @staticmethod
    def get_serializer_data(vote_events):
        ret = []
        for vote_event in vote_events:
            ret.append(dict(
                out_trade_no=vote_event.out_trade_no,
                voter_nickname=vote_event.voter_nickname,
                reach=vote_event.reach,
                gift_name=vote_event.gift_name,
                number_of_gifts=vote_event.number_of_gifts,
                gainer_id=vote_event.candidate.user_id,
                create_time=vote_event.create_time))
        return ret

    def filter_query(self, query):
        form = VoteEventForm(self.request.arguments)
        if form.validate():
            out_trade_no = form.out_trade_no.data
            vote_id = form.vote_id.data
            key = form.key.data
            number = form.number.data
            start_time = form.start_time.data
            end_time = form.end_time.data
            if out_trade_no:
                query = query.where(VoteEvent.out_trade_no == out_trade_no)
            if vote_id:
                query = query.where(VoteEvent.vote_id == vote_id)
            if key:
                query = query.where(User.name.contains(key) | User.nickname.contains(key))
            if number:
                query = query.where(Candidate.number == number)
            if start_time:
                query = query.where(VoteEvent.create_time >= start_time)
            if end_time:
                query = query.where(VoteEvent.create_time <= end_time)
        return query


class VoteListHandler(ListModelMixin, GenericHandler):
    """
    投票列表
    """
    SUPPORTED_METHODS = ('GET', 'OPTIONS')
    query = Vote.admin_vote_list()

    @staticmethod
    def get_serializer_data(votes):
        ret = []
        for vote in votes:
            ret.append(dict(
                id=vote.id,
                title=vote.title,
                description=vote.description,
                start_time=vote.start_time,
                end_time=vote.end_time,
                views=vote.views,
                announcement=vote.announcement,
                total_profit=vote.total_profit,
                total_vote=vote.total_vote,
                total_candidate=vote.total_candidate))
        return ret

    @async_authenticated
    @async_admin_required
    async def post(self, *args, **kwargs):
        param = self.request.body.decode("utf-8")
        data = json.loads(param)
        vote_form = VoteForm.from_json(data)
        if vote_form.validate():
            banners = vote_form.data.pop('banners')
            vote_form.data['cover'] = banners[0]
            vote = await objects.create(Vote, **vote_form.data)
            for banner in banners:
                await objects.create(VoteBanner, vote_id=vote.id, image=banner)
            self.finish(json.dumps(model_to_dict(Vote), default=json_serializer))
        else:
            ret = {}
            self.set_status(400)
            for field in vote_form.errors:
                ret[field] = vote_form.errors[field][0]
            self.finish(ret)


class CandidateStatusHandler(BaseHandler):

    @async_authenticated
    @async_admin_required
    async def put(self, pk, *args, **kwargs):
        try:
            candidate = await objects.get(Candidate, id=pk)
            param = self.request.body.decode("utf-8")
            data = json.loads(param)
            form = CandidateStatusForm.from_json(data)
            if form.validate():
                candidate.is_active = form.is_active.data
                await objects.update(candidate)
                self.finish({'candidate_id': pk, 'is_active': candidate.is_active})
            else:
                self.set_status(400)
                self.finish({'is_active': form.errors['is_active']})

        except Candidate.DoesNotExist:
            raise NotFoundError("参赛选手不存在")
