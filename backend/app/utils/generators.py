from fastapi.routing import APIRoute


# --- UTILIDAD PARA INICIAR LA APP ---
def custom_generate_unique_id(route: APIRoute) -> str:
    # Si la ruta tiene etiquetas, usa la primera. Si no, usa "root".
    tag = route.tags[0] if route.tags else "root"
    return f"{tag}-{route.name}"
