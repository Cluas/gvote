from models import *

GENDERS = (
    ("female", "女"),
    ("male", "男")
)


class User(Model):
    """
    用户模型
    """

    GENDER_CHOICES = (
        (1, '男'),
        (2, '女'),
        (0, '未知'),
    )
    mobile = CharField(max_length=11, verbose_name="手机号码", index=True, unique=True, null=True)
    password = PasswordField(verbose_name="密码", null=True, default='123456')
    openid = CharField(max_length=50, default='', verbose_name="微信openid")
    nickname = CharField(max_length=20, default='', verbose_name="昵称")
    avatar = CharField(max_length=200, default='', verbose_name="头像")
    name = CharField(max_length=6, default='', verbose_name="姓名")
    can_vote = BooleanField(default=True, verbose_name="能否投票")
    gender = SmallIntegerField(choices=GENDER_CHOICES, verbose_name="性别")
    is_staff = BooleanField(default=False, verbose_name="是否是职员")

    @classmethod
    def get_user_info_by_pk(cls, pk):
        return cls.select(
            cls).where(cls.id == pk)

    @classmethod
    def get_vote_rank(cls, candidate_id, rank=5):
        from models.votes import VoteEvent
        vote_rank = (fn.RANK().over(
            order_by=[fn.SUM(VoteEvent.reach)])).alias('vote_rank')
        return cls.select(
            cls,
            fn.SUM(VoteEvent.reach).alias('number_of_votes'),
            vote_rank
        ).join(VoteEvent).where(VoteEvent.candidate_id == candidate_id).group_by(cls.id).limit(rank)

    @classmethod
    def admin_list(cls):
        from models.votes import VoteEvent
        total_cost = fn.COALESCE(fn.SUM(VoteEvent.amount), 0).alias('total_cost')
        query = cls.select(
            cls,
            total_cost
        ).join(VoteEvent, join_type=JOIN.LEFT_OUTER).group_by(cls.id)
        return query
