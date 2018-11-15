from models import *
from models.gifts import Gift
from models.users import User


class Vote(Model):
    """
    投票模型
    """
    announcement = CharField(max_length=200, verbose_name='投票公告', default='')
    title = CharField(max_length=200, verbose_name='投票标题', default='')
    description = CharField(max_length=200, verbose_name='投票描述', default='')
    cover = CharField(max_length=200, verbose_name='封面', default='')
    rules = TextField(verbose_name='奖品和规则', default='')
    views = IntegerField(default=0, verbose_name="访问量")
    start_time = DateTimeField(verbose_name="开始时间")
    end_time = DateTimeField(verbose_name="结束时间")

    @classmethod
    def get_vote_info_by_pk(cls, pk):
        query = cls.select(
            cls.id,
            cls.announcement,
            cls.title,
            cls.description,
            cls.start_time,
            cls.end_time,
            cls.cover,
            cls.views,
            fn.COALESCE(fn.SUM(Candidate.number_of_votes), 0).alias('number_of_votes'),
            fn.COUNT(Candidate.id).alias('number_of_candidates'),
        ).join(Candidate, join_type=JOIN_LEFT_OUTER).where(cls.id == pk)
        return query


class VoteBanner(Model):
    vote = ForeignKeyField(Vote, verbose_name="投票", related_name="banners")
    image = CharField(max_length=200, verbose_name='轮播图', default='')

    class Meta:
        db_table = 'vote_banner'


class Candidate(Model):
    """
    参赛人表
    """
    vote = ForeignKeyField(Vote, related_name='candidates')
    cover = CharField(max_length=200, verbose_name='封面', default='')
    number = CharField(max_length=20, verbose_name='参赛编号')
    number_of_votes = IntegerField(verbose_name='得票数', default=0)
    declaration = CharField(max_length=100, verbose_name='参赛宣言')
    user = ForeignKeyField(User, related_name='votes')
    is_active = BooleanField(default=True, verbose_name="是否可用")

    @classmethod
    def query_candidates_by_vote_id(cls, vote_id):
        diff = (fn.LAG(cls.number_of_votes)
                .over(order_by=[cls.number_of_votes.desc()])
                - cls.number_of_votes)
        vote_rank = (fn.RANK().over(
            order_by=[cls.number_of_votes.desc(), cls.create_time])).alias('vote_rank')
        query = cls.select(
            cls.id,
            cls.cover,
            User.name,
            cls.number,
            cls.number_of_votes,
            cls.declaration,
            fn.COALESCE(diff, 0).alias('diff'),
            vote_rank
        ).join(User).where(cls.vote_id == vote_id, cls.is_active == 1)
        return query

    @classmethod
    def get_vote_info_by_user_id(cls, user_id):
        return cls.select(
            cls.cover,
            Vote.title,
            Vote.description,
            cls.vote_id
        ).join(Vote).where(cls.user_id == user_id)

    class Meta:
        indexes = (
            (("vote", "user"), True),
        )


class VoteEvent(Model):
    """
    礼物事件
    """
    vote = ForeignKeyField(Vote, related_name='events')
    voter = ForeignKeyField(User)
    voter_avatar = CharField(max_length=200, default='', verbose_name="头像")
    voter_nickname = CharField(max_length=20, default='', verbose_name="昵称")
    candidate = ForeignKeyField(Candidate)
    gift = ForeignKeyField(Gift, null=True)
    is_gift = BooleanField(default=False, verbose_name="是否是礼物")
    amount = FloatField(verbose_name='金额')
    image = CharField(max_length=200, verbose_name='礼物图片', default='')
    out_trade_no = CharField(max_length=200, verbose_name='交易单号', default='')
    reach = IntegerField(verbose_name='抵用票数')
    number_of_gifts = IntegerField(verbose_name='礼物数量', default=0)

    @classmethod
    def get_vote_rank(cls, candidate_id, rank=5):
        vote_rank = (fn.RANK().over(
            order_by=[fn.SUM(cls.reach), cls.voter_nickname])).alias('vote_rank')
        return cls.select(
            cls.voter_avatar,
            cls.voter_nickname,
            fn.SUM(cls.reach).alias('number_of_votes'),
            vote_rank
        ).where(cls.candidate_id == candidate_id).group_by(
            cls.voter_id,
            cls.voter_avatar,
            cls.voter_nickname,
        ).limit(rank)

    class Meta:
        db_table = 'vote_event'


class CandidateImage(Model):
    """
    图片
    """
    candidate = ForeignKeyField(Candidate, related_name='images')
    url = CharField(max_length=200, verbose_name="参赛图片")

    class Meta:
        db_table = 'candidate_image'
