
from sqladmin import Admin, ModelView
from app.models.app_setting import AppSetting
from app.services import SettingsService
from app.core.db import engine 


class AppSettingAdmin(ModelView, model=AppSetting):
    column_list = [AppSetting.key, AppSetting.value, AppSetting.description]
    
    form_include_pk = True
    
    # campos del formulario
    form_columns = [
        AppSetting.key,
        AppSetting.value,
        AppSetting.description
    ]

    # Campos que se pueden buscar
    column_searchable_list = [AppSetting.key, AppSetting.description]
    
    name = "Ajuste"
    name_plural = "Ajustes de la Aplicación"
    icon = "fa-solid fa-gear"

    # Hook que se ejecuta después de editar un modelo
    async def after_model_change(self, data: dict, model: AppSetting, is_created: bool, session) -> None:
        # Usamos la sesión del propio hook para instanciar el servicio
        settings_service = SettingsService(session=session)
        settings_service.clear_cache_for_key(model.key)

    # Hook que se ejecuta después de eliminar un modelo
    async def after_model_delete(self, model: AppSetting, session) -> None:
        settings_service = SettingsService(session=session)
        settings_service.clear_cache_for_key(model.key)

def setup_admin(app):
    admin = Admin(app, engine)
    admin.add_view(AppSettingAdmin)
    