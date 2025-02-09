from fastapi import Request, status
from fastapi.responses import JSONResponse
from .exception import UnauthorizedException, DatabaseConnectionError, DatabaseRequestError
from response import ErrorResponse
from qdrant_client.http.exceptions import UnexpectedResponse, ResponseHandlingException


def unauthorized_exception_handler(request: Request, exc: UnauthorizedException):
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=ErrorResponse(
            code=status.HTTP_401_UNAUTHORIZED,
            error="Unauthorized_Error",
            message="Unauthorized"
        ).dict()
    )


def qdrant_client_unexpected_handler(request: Request, exc: UnexpectedResponse):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            code=exc.status_code,
            error="UnexpectedResponse_Error",
            message="Collection doesn't exist!"
        ).dict()
    )


def database_connection_error_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content=ErrorResponse(
            code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error="DatabaseConnectionError",
            message="无法连接到数据库服务。请检查数据库是否正常运行，以及网络连接是否正常。"
        ).dict()
    )


def database_request_error_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error="DatabaseRequestError",
            message=f"数据库请求错误: {str(exc)}"
        ).dict()
    )


def response_handling_exception_handler(request: Request, exc: ResponseHandlingException):
    if "timed out" in str(exc):
        return database_connection_error_handler(request, Exception("Connection timed out"))
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error="DatabaseError",
            message=str(exc)
        ).dict()
    )
