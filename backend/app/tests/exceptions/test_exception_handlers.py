import asyncio

from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from starlette.requests import Request

from app.exceptions.exceptions import (
    _extract_object_from_request,
    generic_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)


def _build_request(path: str, method: str = "GET") -> Request:
    scope = {
        "type": "http",
        "method": method,
        "path": path,
        "headers": [],
        "query_string": b"",
        "client": ("testclient", 50000),
        "scheme": "http",
        "server": ("testserver", 80),
    }
    return Request(scope)


def test_extract_object_from_request_normalizes_path_and_method() -> None:
    request = _build_request("/api/v1/clients/123", method="GET")
    assert _extract_object_from_request(request) == "client.get"


def test_validation_exception_handler_returns_normalized_payload() -> None:
    request = _build_request("/api/v1/users", method="POST")
    exc = RequestValidationError(
        [{"loc": ("body", "email"), "msg": "Field required", "type": "missing"}]
    )

    response = asyncio.run(validation_exception_handler(request, exc))
    payload = response.body.decode("utf-8")

    assert response.status_code == 422
    assert '"object":"user.post"' in payload
    assert '"category":"request_validation"' in payload
    assert "Field 'body.email': Field required" in payload


def test_http_exception_handler_uses_http_metadata() -> None:
    request = _build_request("/api/v1/resources/abc", method="DELETE")
    exc = HTTPException(status_code=404, detail="Not found")

    response = asyncio.run(http_exception_handler(request, exc))
    payload = response.body.decode("utf-8")

    assert response.status_code == 404
    assert '"object":"resource.delete"' in payload
    assert '"category":"http_error"' in payload
    assert '"description":"Not found"' in payload


def test_generic_exception_handler_returns_internal_server_error() -> None:
    request = _build_request("/api/v1/domains", method="PATCH")

    response = asyncio.run(generic_exception_handler(request, RuntimeError("boom")))
    payload = response.body.decode("utf-8")

    assert response.status_code == 500
    assert '"object":"domain.patch"' in payload
    assert '"category":"internal_server_error"' in payload
    assert "unexpected internal server error" in payload.lower()
