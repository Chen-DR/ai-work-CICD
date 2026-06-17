from rest_framework.views import exception_handler
from rest_framework.response import Response


DEFAULT_ERROR_MESSAGES = {
    400: "请求参数不正确",
    401: "请先登录后再继续操作",
    403: "当前账号没有权限执行该操作",
    404: "请求的资源不存在",
    405: "请求方法不被允许",
    500: "服务器内部错误",
}


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        errors = response.data
        code = response.status_code * 100  # map HTTP to business code
        message = DEFAULT_ERROR_MESSAGES.get(response.status_code, "请求处理失败")
        return Response(
            {"code": code, "message": message, "data": errors},
            status=response.status_code,
        )
    return Response(
        {"code": 50001, "message": "服务器内部错误", "data": None},
        status=500,
    )


class BusinessError(Exception):
    def __init__(self, code: int, message: str, data=None):
        self.code = code
        self.message = message
        self.data = data


class SSHConnectionError(BusinessError):
    def __init__(self, message="SSH 连接失败"):
        super().__init__(60001, message)


class SSHDirectoryNotAllowed(BusinessError):
    def __init__(self, message="远程目录不在允许范围内"):
        super().__init__(60002, message)


class SSHCommandRejected(BusinessError):
    def __init__(self, message="命令被安全策略拒绝"):
        super().__init__(60003, message)


class SSHUploadFailed(BusinessError):
    def __init__(self, message="文件上传失败"):
        super().__init__(60004, message)


class SSHDownloadFailed(BusinessError):
    def __init__(self, message="文件下载失败"):
        super().__init__(60005, message)


class DeepSeekError(BusinessError):
    def __init__(self, message="DeepSeek 调用失败"):
        super().__init__(70001, message)


class KnowledgeSearchError(BusinessError):
    def __init__(self, message="知识库检索失败"):
        super().__init__(70002, message)


class FileFormatError(BusinessError):
    def __init__(self, message="文件格式不支持"):
        super().__init__(80001, message)


class FileTooLargeError(BusinessError):
    def __init__(self, message="文件过大"):
        super().__init__(80002, message)
