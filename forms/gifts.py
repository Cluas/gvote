from wtforms import IntegerField
from wtforms.validators import DataRequired

from forms import Form


class GiftSendForm(Form):
    gift_id = IntegerField("礼物ID", validators=[DataRequired(message="礼物必填")])
    num = IntegerField("数量必填", validators=[DataRequired(message="礼物必填")], default=1)