from tornado.web import url

from handlers.auth import JWTTokenHandler, SmsHandler
from handlers.gifts import GiftListHandler, GiftSendHandler, WeixinNotifyHandler, GiftDetailHandler
from handlers.jsapi import WeixinJSAPIHandler
from handlers.oauth import WeixinOAuth2LoginHandler
from handlers.qiniu import QiNiuTokenHandler
from handlers.users import UserInfoHandler, UserListHandler, UserStatusHandler, UserDetailHandler
from handlers.votes import (CandidateListHandler,
                            CandidateDetailHandler,
                            VoteDetailHandler,
                            VoteEventListHandler,
                            VoteRankListHandler,
                            VotingHandler,
                            VoteRoleHandler,
                            VoteEventDetailHandler,
                            VoteListHandler, CandidateStatusHandler, VoteAdminDetailHandler)

urlpatterns = [
    url('/api/v1/tokens/qiniu', QiNiuTokenHandler, name='qiniu_token'),
    url('/api/v1/user_info', UserInfoHandler, name='user_info'),
    url('/api/v1/tokens/jwt', JWTTokenHandler, name='jwt_token'),
    url('/api/v1/votes/([0-9]+)/candidates', CandidateListHandler, name='candidate-list'),
    url('/api/v1/candidates/([0-9]+)/vote_events', VoteEventDetailHandler, name='candidate-vote_event-list'),
    url('/api/v1/candidates/([0-9]+)/vote_ranks', VoteRankListHandler, name='candidate-vote_rank-list'),
    url('/api/v1/gifts', GiftListHandler, name='gift-list'),
    url('/api/v1/candidates/([0-9]+)/gifts', GiftSendHandler, name='send-gift'),
    url('/api/v1/sms', SmsHandler, name='sms'),
    url('/api/v1/votes/([0-9]+)', VoteDetailHandler, name='vote-detail'),
    url('/api/v1/votes/([0-9]+)/rules', VoteRoleHandler, name='vote-rules'),
    url('/api/v1/candidates/([0-9]+)/voting', VotingHandler, name='voting'),
    url('/api/v1/votes/([0-9]+)/candidates/([0-9]+)', CandidateDetailHandler, name='candidate-detail'),
    url('/api/v1/oauth/weixin', WeixinOAuth2LoginHandler, name='oauth_weixin'),
    url('/api/v1/weixin/notify', WeixinNotifyHandler, name='weixin_notify'),
    url('/api/v1/weixin/jsapi', WeixinJSAPIHandler, name='weixin_jsapi'),
    url('/api/v1/admin/orders', VoteEventListHandler, name='order-list'),
    url('/api/v1/admin/votes', VoteListHandler, name='vote-list'),
    url('/api/v1/admin/votes/([0-9]+)', VoteAdminDetailHandler, name='admin-vote-detail'),
    url('/api/v1/admin/users', UserListHandler, name='user-list'),
    url('/api/v1/admin/users/([0-9]+)', UserDetailHandler, name='admin-user-detail'),
    url('/api/v1/admin/users/([0-9]+)/status', UserStatusHandler, name='user-status'),
    url('/api/v1/admin/candidates/([0-9]+)/vote_events', VoteEventDetailHandler, name='admin-candidate-vote_event-list'),
    url('/api/v1/admin/candidates/([0-9]+)/status', CandidateStatusHandler, name='candidate-status'),
    url('/api/v1/admin/gifts/([0-9]+)', GiftDetailHandler, name='admin-gift-detail'),
    url('/api/v1/admin/gifts', GiftListHandler, name='admin-gift-list'),
]
