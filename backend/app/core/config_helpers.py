from __future__ import annotations

import warnings
from typing import Any
from urllib.parse import urlsplit


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


def normalize_minio_endpoint(endpoint: str) -> str:
    """Devuelve solo `host[:port]` para que MinIO/boto3 no reciban path ni scheme."""
    raw_endpoint = endpoint.strip()
    if not raw_endpoint:
        return raw_endpoint

    # Si tiene scheme, parsearlo; si no, asumirlo como host[:port]
    if "://" in raw_endpoint:
        parsed = urlsplit(raw_endpoint)
        netloc = parsed.netloc
    else:
        netloc = raw_endpoint

    # Remover trailing slash y path
    if "/" in netloc:
        netloc = netloc.split("/")[0]

    return netloc.strip()


def resolve_minio_connection(endpoint: str, configured_use_ssl: bool) -> tuple[str, bool]:
    """
    Resuelve el host y el modo SSL efectivo para MinIO.

    Si el endpoint trae scheme explícito (`http://` o `https://`), ese valor
    tiene prioridad sobre `MINIO_USE_SSL` para evitar errores de configuración.
    """
    raw_endpoint = endpoint.strip()
    if not raw_endpoint:
        return raw_endpoint, configured_use_ssl

    parsed = urlsplit(raw_endpoint if "://" in raw_endpoint else f"//{raw_endpoint}")
    host = (parsed.netloc or parsed.path.split("/")[0]).strip()

    if parsed.scheme in {"http", "https"}:
        return host, parsed.scheme == "https"

    return host, configured_use_ssl
