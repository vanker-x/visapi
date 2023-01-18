# Created by Vank
# DateTime: 2022/12/23-16:50
# Encoding: UTF-8
import base64
import json

from itsdangerous import TimestampSigner, BadSignature

from Vank.middleware.base import BaseMiddleware
from Vank.core.config import conf
from Vank.utils.datastructures import Session


class SessionMiddleware(BaseMiddleware):
    def __init__(self, get_response_callable):
        super(SessionMiddleware, self).__init__(get_response_callable)
        self.signer = TimestampSigner(conf.SECRET_KEY)

    def handle_request(self, request, *args, **kwargs):
        # 获取cookie
        signed_session_value = request.cookies.get(conf.SESSION_COOKIE_NAME, "").encode('utf-8')
        # 使用signer进行unsign得到base64编码(压缩原始内容后的编码) 然后将base64编码进行解码得到json序列
        # 再将序列转为python object
        try:
            value = self.signer.unsign(signed_session_value, max_age=conf.SESSION_COOKIE_MAX_AGE)
            session = Session(json.loads(base64.b64decode(value)))
        except BadSignature as e:
            # 如果unsign失败 那么实例化一个空的Session
            session = Session()
        setattr(request, 'session', session)
        return None

    def handle_response(self, request, response):
        session: Session = getattr(request, 'session')
        # 判断此次请求是否有session
        # 如果有session且当前session内容为空
        # 那么将其删除
        if request.cookies.get(conf.SESSION_COOKIE_NAME, None) and not session:
            response.delete_cookie(
                conf.SESSION_COOKIE_NAME,
                conf.SESSION_COOKIE_PATH,
                conf.SESSION_COOKIE_DOMAIN,
                conf.SESSION_COOKIE_SECURE,
                conf.SESSION_COOKIE_HTTP_ONLY,
                conf.SESSION_COOKIE_SAME_SITE,
            )
        # 否则判断session是否改变 如果发生改变 那么重新生成session
        elif session.is_changed and session:
            # 先将数据进行序列化 然后encode为utf-8 再将其压缩为base64编码 然后signer进行sign
            data = base64.b64encode(json.dumps(session.raw).encode("utf-8"))
            data = self.signer.sign(data)
            response.add_cookie(
                conf.SESSION_COOKIE_NAME,
                data.decode(),
                conf.SESSION_COOKIE_MAX_AGE,
                conf.SESSION_COOKIE_EXPIRES,
                conf.SESSION_COOKIE_PATH,
                conf.SESSION_COOKIE_DOMAIN,
                conf.SESSION_COOKIE_SECURE,
                conf.SESSION_COOKIE_HTTP_ONLY,
                conf.SESSION_COOKIE_SAME_SITE,
            )
        return response
