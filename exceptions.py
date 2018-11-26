class APIException(Exception):
    """
    Subclasses should provide `.status_code` and `.default_detail` properties.
    """
    status_code = 500
    default_detail = 'A server error occurred.'
    default_code = 'error'

    def __init__(self, detail=None, code=None):
        if detail is None:
            detail = self.default_detail
        if code is None:
            code = self.default_code

        self.detail = detail
        self.code = code

    def __str__(self):
        return self.detail


class AuthenticationFailed(APIException):
    status_code = 401
    default_detail = '认证失败'
    default_code = 'authentication_failed'


class NotFoundError(APIException):
    status_code = 404
    default_detail = '未找到'
    default_code = 'not_found_error'


class IsVoteError(APIException):
    status_code = 400
    default_detail = '今日已经投票'
    default_code = 'is_vote_error'


class ErrorCode(APIException):
    status_code = 400
    default_detail = '验证码错误'
    default_code = 'error_code'


class DuplicateError(APIException):
    status_code = 400
    default_detail = '不能重复报名'
    default_code = 'duplicate_error'


class WexinError(APIException):
    status_code = 400
    default_detail = '微信错误'
    default_code = 'weixin_error'


class DisableVoting(APIException):
    status_code = 400
    default_detail = '您已经被禁止投票'
    default_code = 'disable_voting'
