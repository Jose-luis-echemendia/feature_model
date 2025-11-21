
# Estructura para Usuarios: (
#    Email, Role
# )

from app.enums import UserRole

users_data = [
    ("echemendiajoseluis@gmail.com", UserRole.ADMIN),
    ("carlos.rodriguez@gmail.com", UserRole.MODEL_DESIGNER),
    ("laura.martinez@gmail.com", UserRole.MODEL_EDITOR),
    ("lianysm99@gmail.com", UserRole.CONFIGURATOR),
    ("yadira.rodriguez@gmail.com", UserRole.VIEWER),
    ("ernesto.lito@gmail.com", UserRole.REVIEWER),
]