from __future__ import annotations

import asyncio
import os
import sys

from app.api.deps import SessionLocal
from app.repositories.domain import DomainRepository
from app.tests.utils.latency import ensure_latency_within_budget, measure_async_latency

DEFAULT_BUDGET_MS = 50.0
DEFAULT_SAMPLE_SIZE = 20
DEFAULT_WARMUP_RUNS = 3


def _env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    return float(value)


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    return int(value)


async def _run() -> None:
    async with SessionLocal() as session:
        repository = DomainRepository(session)
        report = await measure_async_latency(
            repository.count,
            warmup_runs=_env_int("RNF10_WARMUP_RUNS", DEFAULT_WARMUP_RUNS),
            sample_size=_env_int("RNF10_SAMPLE_SIZE", DEFAULT_SAMPLE_SIZE),
        )
        ensure_latency_within_budget(
            report,
            budget_ms=_env_float("RNF10_BUDGET_MS", DEFAULT_BUDGET_MS),
            subject="RNF#10 repositorios → BD",
        )

        print("RNF#10 validado correctamente")
        print(
            "p95="
            f"{report.p95_ms:.2f} ms, avg={report.average_ms:.2f} ms, "
            f"min={report.minimum_ms:.2f} ms, max={report.maximum_ms:.2f} ms"
        )


def main() -> int:
    try:
        asyncio.run(_run())
    except AssertionError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except Exception as exc:  # pragma: no cover - reporte de ejecución manual
        print(f"Error ejecutando RNF#10: {exc}", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
