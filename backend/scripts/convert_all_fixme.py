#!/usr/bin/env python3
"""
Script final para corregir TODAS las estructuras FIXME
Convierte "children": [ ... ] a "groups": [{"type": "XOR/OR", "features": [ ... ]}]
"""

import re


def convert_fixme_to_groups(content):
    """
    Busca patrones con FIXME y convierte la estructura children a groups
    """

    # Patrón para encontrar bloques con FIXME
    # Captura: indentación, tipo de grupo (XOR/OR), y todo hasta el cierre del children

    lines = content.split("\n")
    result_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Detectar línea con FIXME
        if "FIXME" in line:
            # Determinar tipo
            is_xor = "XOR" in line
            group_type = "XOR" if is_xor else "OR"
            min_val = 1
            max_val = 1 if is_xor else 10

            # Limpiar la línea
            clean_line = line.replace(
                '  # FIXME: Debe tener "groups": [{"type": "XOR", ...}]', ""
            )
            clean_line = clean_line.replace(
                '  # FIXME: Debe tener "groups": [{"type": "OR", ...}]', ""
            )
            result_lines.append(clean_line)
            i += 1

            # Copiar líneas hasta encontrar "children":
            while i < len(lines) and '"children"' not in lines[i]:
                result_lines.append(lines[i])
                i += 1

            if i >= len(lines):
                break

            # Procesar la línea con "children":
            children_line = lines[i]
            indent_match = re.match(r"^(\s+)", children_line)
            if not indent_match:
                result_lines.append(children_line)
                i += 1
                continue

            base_indent = indent_match.group(1)

            # Crear estructura groups
            result_lines.append(f'{base_indent}"groups": [')
            result_lines.append(f"{base_indent}    {{")
            result_lines.append(f'{base_indent}        "type": "{group_type}",')
            result_lines.append(f'{base_indent}        "min": {min_val},')
            result_lines.append(f'{base_indent}        "max": {max_val},')
            result_lines.append(f'{base_indent}        "features": [')
            i += 1

            # Copiar todo el contenido hasta encontrar el ] que cierra children
            bracket_count = 1
            while i < len(lines) and bracket_count > 0:
                current_line = lines[i]

                # Contar brackets
                for char in current_line:
                    if char == "[":
                        bracket_count += 1
                    elif char == "]":
                        bracket_count -= 1

                if bracket_count == 0:
                    # Esta es la línea de cierre, modificarla
                    # Quitar el ] final y agregar estructura de cierre
                    stripped = current_line.rstrip()
                    if stripped.endswith("],"):
                        # Reemplazar ], por la estructura de cierre
                        new_line = stripped[:-2]  # Quitar ],
                        result_lines.append(new_line)
                        result_lines.append(f"{base_indent}        ]")
                        result_lines.append(f"{base_indent}    }}")
                        result_lines.append(f"{base_indent}],")
                    elif stripped.endswith("]"):
                        new_line = stripped[:-1]  # Quitar ]
                        result_lines.append(new_line)
                        result_lines.append(f"{base_indent}        ]")
                        result_lines.append(f"{base_indent}    }}")
                        result_lines.append(f"{base_indent}]")
                    else:
                        result_lines.append(current_line)
                else:
                    result_lines.append(current_line)

                i += 1
        else:
            result_lines.append(line)
            i += 1

    return "\n".join(result_lines)


def main():
    filepath = (
        "/home/jose/Escritorio/Work/feature_model/backend/app/seed/data_models.py"
    )

    print("📖 Leyendo archivo...")
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    fixme_count_before = content.count("FIXME")
    print(f"⚠️  Encontrados {fixme_count_before} casos con FIXME")

    print("🔄 Convirtiendo estructuras...")
    new_content = convert_fixme_to_groups(content)

    fixme_count_after = new_content.count("FIXME")
    conversions = fixme_count_before - fixme_count_after

    print(f"✅ Convertidos {conversions} casos")
    print(f"⚠️  Quedan {fixme_count_after} casos sin convertir")

    print("💾 Guardando archivo...")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)

    print("✅ Proceso completado!")


if __name__ == "__main__":
    main()
