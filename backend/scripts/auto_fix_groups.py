#!/usr/bin/env python3
"""
Script para convertir automáticamente estructuras con FIXME
de children a groups
"""

import re


def fix_all_groups(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    i = 0
    changes = 0

    while i < len(lines):
        line = lines[i]

        # Buscar líneas con FIXME
        if "FIXME" in line and "groups" in line:
            # Determinar si es XOR u OR
            if "XOR" in line:
                group_type = "XOR"
                min_val, max_val = 1, 1
            else:
                group_type = "OR"
                min_val, max_val = 1, 10

            # Obtener la indentación
            indent_match = re.match(r"^(\s+)", line)
            if indent_match:
                indent = indent_match.group(1)

                # Limpiar el FIXME comment
                lines[i] = lines[i].replace(
                    '  # FIXME: Debe tener "groups": [{"type": "XOR", ...}]', ""
                )
                lines[i] = lines[i].replace(
                    '  # FIXME: Debe tener "groups": [{"type": "OR", ...}]', ""
                )

                # Buscar la línea con "children": [
                j = i + 1
                while j < len(lines) and '"children":' not in lines[j]:
                    j += 1

                if j < len(lines):
                    # Reemplazar "children": [ por "groups": [
                    children_line = lines[j]
                    children_indent = re.match(r"^(\s+)", children_line).group(1)

                    # Insertar la estructura de groups
                    new_lines = [
                        f'{children_indent}"groups": [\n',
                        f"{children_indent}    {{\n",
                        f'{children_indent}        "type": "{group_type}",\n',
                        f'{children_indent}        "min": {min_val},\n',
                        f'{children_indent}        "max": {max_val},\n',
                        f'{children_indent}        "features": [\n',
                    ]

                    # Encontrar el cierre del children
                    bracket_count = 0
                    k = j
                    found_open = False

                    while k < len(lines):
                        for char in lines[k]:
                            if char == "[":
                                bracket_count += 1
                                found_open = True
                            elif char == "]":
                                bracket_count -= 1
                                if found_open and bracket_count == 0:
                                    # Encontramos el cierre
                                    # Insertar cierre de groups
                                    close_pos = lines[k].index("]")
                                    lines[k] = (
                                        lines[k][:close_pos]
                                        + f"{children_indent}        ]\n{children_indent}    }}\n{children_indent}"
                                        + lines[k][close_pos:]
                                    )
                                    break
                        if found_open and bracket_count == 0:
                            break
                        k += 1

                    # Reemplazar la línea de children con groups
                    lines[j] = "".join(new_lines)
                    changes += 1

        i += 1

    # Guardar
    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(lines)

    print(f"✅ Convertidos {changes} casos de children → groups")


if __name__ == "__main__":
    filepath = (
        "/home/jose/Escritorio/Work/feature_model/backend/app/seed/data_models.py"
    )
    fix_all_groups(filepath)
