from __future__ import annotations

from datetime import datetime, date
from typing import Any, Optional, Union

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.api.errors import ErrorCode, DEFAULT_MESSAGES

JsonExclude = Optional[Union[set[str], dict[str, Any]]]


def _default_datetime_encoder(fmt: str):
    def _encode(value: Union[datetime, date]) -> str:
        if isinstance(value, datetime):
            return value.strftime(fmt)
        return datetime(value.year, value.month, value.day).strftime(fmt)

    return _encode


def _encode_payload(
    data: Any,
    *,
    exclude: JsonExclude = None,
    datetime_format: str,
) -> Any:
    custom = {
        datetime: _default_datetime_encoder(datetime_format),
        date: _default_datetime_encoder(datetime_format),
    }

    if isinstance(data, (list, tuple)):
        return [
            jsonable_encoder(item, custom_encoder=custom, exclude=exclude)
            for item in data
        ]

    return jsonable_encoder(data, custom_encoder=custom, exclude=exclude)


def _reformat_datetime_strings(obj: Any, fmt: str) -> Any:
    if isinstance(obj, dict):
        return {k: _reformat_datetime_strings(v, fmt) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_reformat_datetime_strings(v, fmt) for v in obj]
    if isinstance(obj, tuple):
        return tuple(_reformat_datetime_strings(v, fmt) for v in obj)
    if isinstance(obj, (datetime, date)):
        return _default_datetime_encoder(fmt)(obj)
    if isinstance(obj, str):
        s = obj
        try:
            if s.endswith("Z"):
                s = s[:-1] + "+00:00"
            dt = datetime.fromisoformat(s)
            return dt.strftime(fmt)
        except Exception:
            return obj
    return obj


def success(
    data: Any = None,
    *,
    message: str = "success",
    code: int = 0,
    exclude: JsonExclude = None,
    datetime_format: str = "%Y-%m-%d %H:%M:%S",
    status_code: int = 200,
) -> JSONResponse:
    payload = {
        "code": code,
        "message": message,
        "data": _encode_payload(data, exclude=exclude, datetime_format=datetime_format),
    }
    payload = _reformat_datetime_strings(payload, datetime_format)
    return JSONResponse(content=payload, status_code=status_code)


def error(
    *,
    message: str = "error",
    code: int = -1,
    data: Any = None,
    exclude: JsonExclude = None,
    datetime_format: str = "%Y-%m-%d %H:%M:%S",
    status_code: int = 400,
) -> JSONResponse:
    payload = {
        "code": code,
        "message": message,
        "data": _encode_payload(data, exclude=exclude, datetime_format=datetime_format),
    }
    payload = _reformat_datetime_strings(payload, datetime_format)
    return JSONResponse(content=payload, status_code=status_code)


def error_code(
    *,
    code: ErrorCode,
    data: Any = None,
    message: Optional[str] = None,
    datetime_format: str = "%Y-%m-%d %H:%M:%S",
    status_code: int = 400,
) -> JSONResponse:
    msg = message if message is not None else DEFAULT_MESSAGES[code]
    return error(
        message=msg,
        code=int(code),
        data=data,
        datetime_format=datetime_format,
        status_code=status_code,
    )


