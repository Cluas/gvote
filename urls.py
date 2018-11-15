from tornado.web import url

from handlers.auth import JWTTokenHandler, SmsHandler
from handlers.gifts import GiftListHandler, GiftSendHandler
from handlers.oauth import WeixinOAuth2LoginHandler
from handlers.qiniu import QiNiuTokenHandler
from handlers.users import UserInfoHandler
from handlers.votes import CandidateListHandler, CandidateDetailHandler, VoteDetailHandler, VoteEventListHandler, \
    VoteRankListHandler, VotingHandler, VoteRoleHandler

urlpatterns = [
    url('/api/v1/tokens/qiniu', QiNiuTokenHandler, name='qiniu_token'),
    url('/api/v1/user_info', UserInfoHandler, name='user_info'),
    url('/api/v1/tokens/jwt', JWTTokenHandler, name='jwt_token'),
    url('/api/v1/candidates', CandidateListHandler, name='candidate-list'),
    url('/api/v1/candidates/([0-9]+)/vote_events', VoteEventListHandler, name='candidate-vote_event-list'),
    url('/api/v1/candidates/([0-9]+)/vote_ranks', VoteRankListHandler, name='candidate-vote_rank-list'),
    url('/api/v1/gifts', GiftListHandler, name='gift-list'),
    url('/api/v1/candidates/([0-9]+)/gifts', GiftSendHandler, name='gift-list'),
    url('/api/v1/sms', SmsHandler, name='sms'),
    url('/api/v1/votes/([0-9]+)', VoteDetailHandler, name='vote-detail'),
    url('/api/v1/votes/([0-9]+)/rules', VoteRoleHandler, name='vote-rules'),
    url('/api/v1/candidates/([0-9]+)/voting', VotingHandler, name='voting'),
    url('/api/v1/candidates/([0-9]+)', CandidateDetailHandler, name='candidate-detail'),
    url('/api/v1/oauth/weixin', WeixinOAuth2LoginHandler, name='oauth_weixin'),
]

