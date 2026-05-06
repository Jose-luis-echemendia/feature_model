from __future__ import annotations

from dataclasses import dataclass
from math import ceil
from statistics import mean
from time import perf_counter_ns
from typing import Awaitable, Callable, Sequence, TypeVar

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class LatencyReport:
    samples_ms: tuple[float, ...]
    p95_ms: float
    average_ms: float
    minimum_ms: float
    maximum_ms: float


async def measure_async_latency(
    operation: Callable[[], Awaitable[T]],
    *,
    warmup_runs: int = 3,
    sample_size: int = 20,
) -> LatencyReport:
    """Mide la latencia de una operación asíncrona y calcula métricas básicas."""
    if warmup_runs < 0:
        raise ValueError("warmup_runs must be greater than or equal to zero")
    if sample_size <= 0:
        raise ValueError("sample_size must be greater than zero")

    for _ in range(warmup_runs):
        await operation()

    samples_ms: list[float] = []
    for _ in range(sample_size):
        start_ns = perf_counter_ns()
        await operation()
        elapsed_ms = (perf_counter_ns() - start_ns) / 1_000_000
        samples_ms.append(elapsed_ms)

    ordered_samples = sorted(samples_ms)
    p95_index = max(0, ceil(0.95 * len(ordered_samples)) - 1)

    return LatencyReport(
        samples_ms=tuple(samples_ms),
        p95_ms=ordered_samples[p95_index],
        average_ms=mean(samples_ms),
        minimum_ms=min(samples_ms),
        maximum_ms=max(samples_ms),
    )


def format_latency_report(report: LatencyReport) -> str:
    """Genera un resumen legible del reporte de latencia."""
    samples = ", ".join(f"{sample:.2f}" for sample in report.samples_ms)
    return (
        f"p95={report.p95_ms:.2f} ms, avg={report.average_ms:.2f} ms, "
        f"min={report.minimum_ms:.2f} ms, max={report.maximum_ms:.2f} ms, "
        f"samples=[{samples}]"
    )


def ensure_latency_within_budget(
    report: LatencyReport,
    *,
    budget_ms: float,
    subject: str,
) -> None:
    """Falla con un mensaje descriptivo cuando la latencia excede el presupuesto."""
    if report.p95_ms > budget_ms:
        raise AssertionError(
            f"{subject}: p95={report.p95_ms:.2f} ms supera el presupuesto de "
            f"{budget_ms:.2f} ms. {format_latency_report(report)}"
        )
