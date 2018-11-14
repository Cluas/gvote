from forms import Form
from wtforms import StringField, FieldList, IntegerField
from wtforms.validators import DataRequired, Regexp

MOBILE_REGEX = "^1[358]\d{9}$|^1[48]7\d{8}$|^176\d{8}$"


class CandidateForm(Form):
    mobile = StringField("手机号码", validators=[Regexp(MOBILE_REGEX, message="请输入合法的手机号码")])
    code = StringField("验证码")
    name = StringField("姓名")
    declaration = StringField("参赛宣言", validators=[DataRequired(message="参赛宣言")])
    vote_id = IntegerField("参赛投票", validators=[DataRequired(message="投票ID是必填的")])
    images = FieldList(StringField("参赛图片", validators=[DataRequired(message="请输入参赛图片列表")]))
