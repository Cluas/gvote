from wtforms import IntegerField, StringField, FloatField
from wtforms.validators import DataRequired, Length

from forms import Form


class GiftSendForm(Form):
    gift_id = IntegerField("礼物ID", validators=[DataRequired(message="礼物必填")])
    num = IntegerField("数量必填", validators=[DataRequired(message="礼物必填")], default=1)


class GiftForm(Form):
    name = StringField('礼物名称', validators=[DataRequired(message='礼物名称是必填的'), Length(max=15)])
    image = StringField('礼物图片', validators=[DataRequired(message='礼物图片是必填的'), Length(max=200)])
    reach = IntegerField('抵用票数', validators=[DataRequired(message='抵用票数是必填的')])
    price = FloatField('价格', validators=[DataRequired(message='价格是必填的')])
