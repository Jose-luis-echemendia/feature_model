#!/usr/bin/env python3
"""Conventional Commit message validator.

This script is intended to be used as a commit-msg hook.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ALLOWED_TYPES = (
    "build",
    "chore",
    "ci",
    "docs",
    "feat",
    "fix",
    "perf",
    "refactor",
    "revert",
    "style",
    "test",
)

TYPE_GROUP = "|".join(ALLOWED_TYPES)

CONVENTIONAL_RE = re.compile(rf"^(?:{TYPE_GROUP})(?:\([a-z0-9._-]+\))?(!)?:\s+.+$")

MERGE_RE = re.compile(r"^Merge\s+")
REVERT_RE = re.compile(r'^Revert\s+".+"$')


def _first_non_comment_line(message: str) -> str | None:
    for line in message.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        return stripped
    return None


def main() -> int:
    if len(sys.argv) < 2:
        print("Falta la ruta del archivo de mensaje de commit.")
        return 1

    message_path = Path(sys.argv[1])
    if not message_path.exists():
        print("No se encontró el archivo de mensaje de commit.")
        return 1

    message = message_path.read_text(encoding="utf-8")
    first_line = _first_non_comment_line(message)

    if not first_line:
        print("El mensaje de commit no puede estar vacío.")
        return 1

    if MERGE_RE.match(first_line) or REVERT_RE.match(first_line):
        return 0

    if not CONVENTIONAL_RE.match(first_line):
        allowed = ", ".join(ALLOWED_TYPES)
        print("Formato de commit inválido. Usa Conventional Commits.")
        print(f"Tipos permitidos: {allowed}")
        print("Ejemplos válidos:")
        print("  feat(api): agregar endpoint de reportes")
        print("  fix: corregir validación de email")
        print("  refactor(auth)!: simplificar flujo de login")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
