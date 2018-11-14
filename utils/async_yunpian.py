import json
from random import choice
from urllib.parse import urlencode

from tornado import httpclient
from tornado.httpclient import HTTPRequest


def generate_code(digit=4):
    """
    生成随机digit位数字的验证码
    :return:
    """
    seeds = "1234567890"
    random_str = []
    for i in range(digit):
        random_str.append(choice(seeds))
    return "".join(random_str)


class AsyncYunpian:
    def __init__(self, api_key):
        self.api_key = api_key

    async def send_single_sms(self, code, mobile):
        http_client = httpclient.AsyncHTTPClient()
        url = "https://sms.yunpian.com/v2/sms/single_send.json"
        text = "【慕学生鲜】您的验证码是{}。如非本人操作，请忽略本短信".format(code)
        post_request = HTTPRequest(url=url, method="POST", body=urlencode({
            "apikey": self.api_key,
            "mobile": mobile,
            "text": text
        }))
        res = await http_client.fetch(post_request)
        return json.loads(res.body.decode("utf8"))


yunpian = AsyncYunpian("d6c4ddbf50ab36611d2f52041a0b949e")
if __name__ == "__main__":
    import tornado

    io_loop = tornado.ioloop.IOLoop.current()

    yunpian = AsyncYunpian("d6c4ddbf50ab36611d2f52041a0b949e")

    # run_sync方法可以在运行完某个协程之后停止事件循环
    from functools import partial

    new_func = partial(yunpian.send_single_sms, "1234", "18785625498")
    io_loop.run_sync(new_func)
