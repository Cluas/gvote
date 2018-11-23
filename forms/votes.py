from forms import Form
from wtforms import StringField, FieldList, IntegerField, DateTimeField, BooleanField, Field
from wtforms.validators import DataRequired, Regexp, Length

MOBILE_REGEX = "^1[358]\d{9}$|^1[48]7\d{8}$|^176\d{8}$"


class CandidateForm(Form):
    mobile = StringField("手机号码", validators=[Regexp(MOBILE_REGEX, message="请输入合法的手机号码")])
    code = StringField("验证码")
    name = StringField("姓名")
    declaration = StringField("参赛宣言", validators=[DataRequired(message="参赛宣言")])
    images = FieldList(StringField("参赛图片", validators=[DataRequired(message="请输入参赛图片列表")]))


class CandidateStatusForm(Form):
    is_active = BooleanField("是否能投票")


class VoteEventForm(Form):
    out_trade_no = StringField("订单编号")
    vote_id = IntegerField("活动id")
    key = StringField("搜索关键字")
    number = StringField("参赛编号")
    start_time = DateTimeField("开始时间")
    end_time = DateTimeField("结束时间")


class VoteForm(Form):
    announcement = StringField('投票公告', validators=[Length(max=200), DataRequired(message="请输入投票公告")])
    title = StringField('投票标题', validators=[Length(max=200), DataRequired(message="请输入投票标题")])
    description = StringField('投票描述', validators=[Length(max=200), DataRequired(message="请输入投票描述")])
    rules = StringField('奖品和规则', validators=[DataRequired(message="请输入奖品和规则")])
    start_time = DateTimeField("开始时间", validators=[DataRequired(message="请输入开始时间")])
    end_time = DateTimeField("结束时间", validators=[DataRequired(message="请输入结束时间")])
    banners = FieldList(Field("宣传海报", validators=[DataRequired(message="请输入宣传海报列表")]))


class VoteUpdateForm(Form):
    announcement = StringField('投票公告', validators=[Length(max=200)])
    title = StringField('投票标题', validators=[Length(max=200)])
    description = StringField('投票描述', validators=[Length(max=200)])
    rules = StringField('奖品和规则')
    start_time = DateTimeField("开始时间")
    end_time = DateTimeField("结束时间")
    banners = FieldList(Field("宣传海报"))
