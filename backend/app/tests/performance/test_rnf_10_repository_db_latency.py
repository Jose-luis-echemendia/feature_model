"""Compatibilidad histórica para el benchmark RNF#10.

Este módulo ya no define pruebas de pytest; ahora actúa como lanzador fino del
script ejecutable ubicado en `backend/scripts/check_rnf_10_latency.py`.
"""

from scripts.check_rnf_10_latency import main

if __name__ == "__main__":
    raise SystemExit(main())
