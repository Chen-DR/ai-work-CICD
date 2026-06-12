from rest_framework.views import exception_handler
from rest_framework.response import Response


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        errors = response.data
        code = response.status_code * 100  # map HTTP to business code
        return Response(
            {"code": code, "message": str(exc), "data": errors},
            status=response.status_code,
        )
    return Response(
        {"code": 50001, "message": "Internal server error", "data": None},
        status=500,
    )


class BusinessError(Exception):
    def __init__(self, code: int, message: str, data=None):
        self.code = code
        self.message = message
        self.data = data


class SSHConnectionError(BusinessError):
    def __init__(self, message="SSH connection failed"):
        super().__init__(60001, message)


class SSHDirectoryNotAllowed(BusinessError):
    def __init__(self, message="Remote directory not allowed"):
        super().__init__(60002, message)


class SSHCommandRejected(BusinessError):
    def __init__(self, message="Command rejected by security policy"):
        super().__init__(60003, message)


class SSHUploadFailed(BusinessError):
    def __init__(self, message="File upload failed"):
        super().__init__(60004, message)


class SSHDownloadFailed(BusinessError):
    def __init__(self, message="File download failed"):
        super().__init__(60005, message)


class DeepSeekError(BusinessError):
    def __init__(self, message="DeepSeek API call failed"):
        super().__init__(70001, message)


class KnowledgeSearchError(BusinessError):
    def __init__(self, message="Knowledge search failed"):
        super().__init__(70002, message)


class FileFormatError(BusinessError):
    def __init__(self, message="File format not supported"):
        super().__init__(80001, message)


class FileTooLargeError(BusinessError):
    def __init__(self, message="File too large"):
        super().__init__(80002, message)
