"""Script simple para detectar operaciones peligrosas en archivos de Alembic.


Busca patrones que podrían causar rewrite o locks largos:
- ADD COLUMN .* NOT NULL
- ADD COLUMN .* DEFAULT [^NULL]
- ALTER COLUMN .* TYPE
- DROP COLUMN


Este script es un detector básico: actúa como gate en CI y puede adaptarse.
"""
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERSIONS = ROOT / 'alembic' / 'versions'


DANGEROUS_PATTERNS = [
    re.compile(r"ADD\s+COLUMN.+NOT\s+NULL", re.IGNORECASE),
    re.compile(r"ADD\s+COLUMN.+DEFAULT", re.IGNORECASE),
    re.compile(r"ALTER\s+COLUMN.+TYPE", re.IGNORECASE),
    re.compile(r"DROP\s+COLUMN", re.IGNORECASE),
]


issues = []
for f in VERSIONS.glob('*.py'):
    text = f.read_text(encoding='utf-8')
    for pat in DANGEROUS_PATTERNS:
        if pat.search(text):
            issues.append((f.relative_to(ROOT), pat.pattern))


if issues:
    print("Se encontraron operaciones potencialmente peligrosas en migraciones:")
    for file, pat in issues:
        print(f" - {file} => {pat}")
    print("\nSi estas operaciones son intencionales, documenta el plan EMC en el PR.\n")
    sys.exit(2)
else:
    print("No se encontraron patrones peligrosos (check básico).")
    sys.exit(0)