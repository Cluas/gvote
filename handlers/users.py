import json

from handlers.base import BaseHandler

import logging

from models.users import User
from models.votes import Candidate
from utils.decorators import async_authenticated

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

        user_info = await User.objects.execute(query)
        user_info = user_info[0]
        votes_query = Candidate.get_vote_info_by_user_id(user.id)

        candidates = await Candidate.objects.execute(votes_query)

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
        ranks = await User.objects.execute(query)

        ret = []
        for rank in ranks:
            ret.append(dict(
                voter_avatar=rank.avatar,
                voter_nickname=rank.nickname,
                number_of_votes=int(rank.number_of_votes),
                vote_rank=rank.vote_rank
            ))
        self.finish(json.dumps(ret))
