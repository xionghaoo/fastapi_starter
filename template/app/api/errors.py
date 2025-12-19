from enum import IntEnum
from fastapi import status


class ErrorCode(IntEnum):
    UNKNOWN_ERROR = -1000

    @staticmethod
    def error_doc() -> str:
        return (
            "- Authorization header: `Authorization: bearer {token}`\n"
            "- Unified response: `{ \"code\": 0, \"message\": \"success\", \"data\": { ... } }`;\n"
            "  non-zero code indicates error.\n"
            "- Error codes:\n"
            "   - `0`: success\n"
            f"  - `{ErrorCode.UNKNOWN_ERROR}`: unknown error\n"
        )


class BusinessError(Exception):
    def __init__(self, *, code: int, message: str, status_code: int = status.HTTP_400_BAD_REQUEST) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


DEFAULT_MESSAGES = {
    ErrorCode.UNKNOWN_ERROR: "Unknown error"
}


