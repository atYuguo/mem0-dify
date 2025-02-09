from fastapi import HTTPException, status


class ErrorHttpException(HTTPException):
    code: int
    error: str
    message: str

    def __init__(self, code: int = 500, error: str = "INTERNAL_SERVER_ERROR",
                 message: str = "INTERNAL_SERVER_ERROR") -> None:
        super().__init__(
            status_code=200,
            detail={"code": code, "error": error, "message": message},
        )
        self.code = code
        self.error = error
        self.message = message


class UnauthorizedException(ErrorHttpException):
    def __init__(self):
        super().__init__(
            code=status.HTTP_401_UNAUTHORIZED,
            message="UNAUTHORIZED",
            error="Authorization_Error"
        )


class DatabaseConnectionError(ErrorHttpException):
    def __init__(self):
        super().__init__(
            code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error="DatabaseConnectionError",
            message="无法连接到数据库服务。请检查数据库是否正常运行，以及网络连接是否正常。"
        )


class DatabaseRequestError(ErrorHttpException):
    def __init__(self, message: str):
        super().__init__(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error="DatabaseRequestError",
            message=f"数据库请求错误: {message}"
        )
