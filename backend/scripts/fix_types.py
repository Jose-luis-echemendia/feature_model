#!/usr/bin/env python3
"""
Script para corregir los tipos incorrectos en data_models.py

Convierte:
- FeatureType.XOR_GROUP → estructura con groups: [{type: "XOR", ...}]
- FeatureType.OR_GROUP → estructura con groups: [{type: "OR", ...}]
- FeatureType.ALTERNATIVE → FeatureType.OPTIONAL (dentro de grupos)
"""

import re
import sys


def fix_data_models(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Contador de cambios
    changes = 0

    # 1. Eliminar imports incorrectos de FeatureType que no existen
    # No hay XOR_GROUP, OR_GROUP, ALTERNATIVE en el enum FeatureType

    # 2. Cambiar FeatureType.ALTERNATIVE a FeatureType.OPTIONAL
    # Esto aplica a features dentro de grupos
    pattern_alternative = r"FeatureType\.ALTERNATIVE"
    content, count = re.subn(pattern_alternative, "FeatureType.OPTIONAL", content)
    changes += count
    print(
        f"✅ Cambiados {count} casos de FeatureType.ALTERNATIVE → FeatureType.OPTIONAL"
    )

    # 3. NO cambiar los strings "XOR" y "OR" que ya son correctos en groups
    # Esos ya están bien como "type": "XOR"

    # 4. Los casos de XOR_GROUP y OR_GROUP necesitan reestructuración manual
    # Por ahora solo reportar dónde están
    xor_group_matches = list(re.finditer(r"FeatureType\.XOR_GROUP", content))
    or_group_matches = list(re.finditer(r"FeatureType\.OR_GROUP", content))

    if xor_group_matches:
        print(
            f"\n⚠️  Encontrados {len(xor_group_matches)} casos de FeatureType.XOR_GROUP que requieren reestructuración manual"
        )
        for i, match in enumerate(xor_group_matches[:5], 1):
            line_num = content[: match.start()].count("\n") + 1
            print(f"    Línea {line_num}")

    if or_group_matches:
        print(
            f"\n⚠️  Encontrados {len(or_group_matches)} casos de FeatureType.OR_GROUP que requieren reestructuración manual"
        )
        for i, match in enumerate(or_group_matches[:5], 1):
            line_num = content[: match.start()].count("\n") + 1
            print(f"    Línea {line_num}")

    # Guardar cambios
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"\n✅ Total de cambios aplicados: {changes}")
    return changes


if __name__ == "__main__":
    filepath = (
        "/home/jose/Escritorio/Work/feature_model/backend/app/seed/data_models.py"
    )
    fix_data_models(filepath)
