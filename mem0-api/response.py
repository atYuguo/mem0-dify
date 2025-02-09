from pydantic import BaseModel
from typing import Any, Literal
from typing_extensions import TypedDict
import qdrant_client.http.exceptions


class SuccessfulResponse(BaseModel):
    code: int = 0
    data: Any = None


class ErrorResponse(BaseModel):
    code: int = 500
    error: str = "INTERNAL_SERVER_ERROR"
    message: str = "INTERNAL_SERVER_ERROR"
    details: Any = None

    @classmethod
    def from_exception(cls, exc: Exception) -> "ErrorResponse":
        if isinstance(exc, qdrant_client.http.exceptions.ResponseHandlingException):
            return cls(
                code=503,
                error="DATABASE_CONNECTION_ERROR",
                message="Failed to connect to vector database",
                details=str(exc)
            )
        return cls(
            message=str(exc),
            details=type(exc).__name__
        )


class StoreMemoryResponse(SuccessfulResponse):
    class StoreMemoryExecuteResult(TypedDict):
        id: str
        event: str
        data: str

    def __init__(self, execute_result: StoreMemoryExecuteResult):
        super().__init__(
            data=execute_result
        )
