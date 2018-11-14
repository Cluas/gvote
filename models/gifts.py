from models import *


class Gift(Model):
    """
    礼物
    """
    name = CharField(max_length=15, verbose_name='礼物名称')
    image = CharField(max_length=200, verbose_name='礼物图片')
    reach = IntegerField(verbose_name='抵用票数')
    price = FloatField(verbose_name='价格')
