import json
import logging

from exceptions import NotFoundError
from forms.users import UserStatusForm
from handlers.base import BaseHandler, GenericHandler
from mixins import ListModelMixin
from models import objects
from models.users import User
from models.votes import Candidate, CandidateImage
from utils.decorators import async_authenticated, async_admin_required
from utils.json import json_serializer

logger = logging.getLogger('vote.' + __name__)


class UserInfoHandler(BaseHandler):
    """
    用户个人信息接口
    """
    SUPPORTED_METHODS = ('GET', 'OPTIONS')

    @async_authenticated
    async def get(self, *args, **kwargs):
        user = self.current_user
        query = User.get_user_info_by_pk(user.id)

        user_info = await objects.execute(query)
        user_info = user_info[0]
        votes_query = Candidate.get_vote_info_by_user_id(user.id)

        candidates = await objects.execute(votes_query)

        votes = [{'title': candidate.vote.title,
                  'description': candidate.vote.description,
                  'vote_id': candidate.vote_id,
                  'cover': candidate.cover} for candidate in candidates]
        ret = dict(
            avatar=user_info.avatar,
            nickname=user_info.nickname,
            name=user_info.name,
            mobile=user_info.mobile[:3] + '****' + user_info.mobile[-4:] if user_info.mobile else '',
            votes=votes
        )
        self.finish(ret)


class VoteRankListHandler(BaseHandler):
    """
    用户投票贡献排行
    """
    SUPPORTED_METHODS = ('GET', 'OPTIONS')

    async def get(self, candidate_id, *args, **kwargs):
        query = User.get_vote_rank(candidate_id)
        print(query.sql()[0])
        ranks = await objects.execute(query)

        ret = []
        for rank in ranks:
            ret.append(dict(
                voter_avatar=rank.avatar,
                voter_nickname=rank.nickname,
                number_of_votes=int(rank.number_of_votes),
                vote_rank=rank.vote_rank
            ))
        self.finish(json.dumps(ret))


class UserListHandler(ListModelMixin, GenericHandler):
    """
    用户列表
    """
    query = User.admin_list()
    SUPPORTED_METHODS = ('GET', 'OPTIONS')

    @async_authenticated
    @async_admin_required
    async def get(self, *args, **kwargs):
        await super().get(*args, **kwargs)

    @staticmethod
    def get_serializer_data(users):
        ret = []
        for user in users:
            ret.append(dict(
                id=user.id,
                nickname=user.nickname,
                name=user.name,
                avatar=user.avatar,
                total_cost=user.total_cost,
                mobile=user.mobile))
        return ret

    def filter_query(self, query):
        vote_id = self.get_argument('vote_id', '')
        key = self.get_argument('key', '')

        if vote_id:
            query = query.switch(User).join(Candidate).where(Candidate.vote_id == vote_id)
        if key:
            query = query.where(User.name.contains(key) | User.nickname.contains(key) | User.mobile.contains(key))
        return query


class UserStatusHandler(BaseHandler):

    @async_authenticated
    @async_admin_required
    async def put(self, user_id, *args, **kwargs):
        try:
            user = await objects.get(User, id=user_id)
            param = self.request.body.decode("utf-8")
            data = json.loads(param)
            form = UserStatusForm.from_json(data)
            if form.validate():
                user.can_vote = form.can_vote.data
                await objects.update(user)
                self.finish({'user_id': user_id, 'can_vote': user.can_vote})
            else:
                self.set_status(400)
                self.finish({'can_vote': form.errors['can_vote']})

        except User.DoesNotExist:
            raise NotFoundError("用户不存在")


class UserDetailHandler(BaseHandler):

    @async_authenticated
    @async_admin_required
    async def get(self, user_id, *args, **kwargs):
        try:
            user = await objects.get(User, id=user_id)
            votes_query = Candidate.get_admin_vote_info(user.id)

            candidates = await objects.prefetch(votes_query, CandidateImage.select())

            votes = [{'title': candidate.vote.title,
                      'description': candidate.vote.description,
                      'vote_id': candidate.vote.id,
                      'cover': candidate.cover,
                      'declaration': candidate.declaration,
                      'registration_time': candidate.create_time,
                      'vote_start_time': candidate.vote.start_time,
                      'vote_end_time': candidate.vote.end_time,
                      'total_vote': candidate.total_vote,
                      'total_profit': candidate.total_profit,
                      'images': [image.url for image in candidate.images],
                      'id': candidate.id} for candidate in candidates]
            ret = dict(
                avatar=user.avatar,
                nickname=user.nickname,
                name=user.name,
                mobile=user.mobile[:3] + '****' + user.mobile[-4:] if user.mobile else '',
                votes=votes
            )
            self.finish(json.dumps(ret, default=json_serializer))

        except User.DoesNotExist:
            raise NotFoundError("用户不存在")
