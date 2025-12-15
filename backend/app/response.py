
from fastapi.responses import JSONResponse

from app.models.common import SuccessResponse

# Clase de respuesta personalizada para los éxitos
class UnifiedResponse(JSONResponse):
    def __init__(self, content, object_name: str, status_code: int = 200, **kwargs):
        # Creamos la estructura de éxito
        response_data = SuccessResponse[type(content)](
            object=object_name,
            code=status_code,
            data=content
        )
        # Convertimos el modelo Pydantic a un diccionario y lo pasamos a la clase padre
        super().__init__(content=response_data.model_dump(), status_code=status_code, **kwargs)