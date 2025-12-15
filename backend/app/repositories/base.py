class BaseUserRepository:

    def validate_email_unique(self, existing_user):
        if existing_user:
            raise ValueError("El email ya está registrado.")

    def prepare_password(self, password: str) -> str:
        from app.core.security import get_password_hash

        return get_password_hash(password)

    def _set_active_status(self, user, is_active: bool):
        """Helper para establecer el estado is_active de un usuario."""
        user.is_active = is_active


class BaseDomainRepository:
    """Clase base con lógica compartida para repositorios de dominios."""

    def validate_name_unique(self, existing_domain, current_domain_id=None):
        """Valida que el nombre del dominio sea único."""
        if existing_domain:
            # Si estamos actualizando, permitir el mismo nombre si es el mismo dominio
            if current_domain_id and existing_domain.id == current_domain_id:
                return
            raise ValueError(
                f"Ya existe un dominio con el nombre: {existing_domain.name}"
            )

    def _set_active_status(self, entity, is_active: bool):
        """Helper para establecer el estado is_active de una entidad."""
        entity.is_active = is_active


class BaseFeatureModelRepository:
    """Clase base con lógica compartida para repositorios de feature models."""

    def validate_name_unique_in_domain(
        self, existing_model, current_model_id=None, name=None
    ):
        """Valida que el nombre del feature model sea único dentro del dominio."""
        if existing_model:
            # Si estamos actualizando, permitir el mismo nombre si es el mismo modelo
            if current_model_id and existing_model.id == current_model_id:
                return
            raise ValueError(
                f"Ya existe un Feature Model con el nombre '{name or existing_model.name}' en este dominio."
            )


class BaseFeatureRepository:
    """Clase base con lógica compartida para repositorios de features."""

    def validate_parent_not_self(self, feature_id, parent_id):
        """Valida que una feature not pueda ser su propio padre."""
        if parent_id and feature_id == parent_id:
            raise ValueError("A feature cannot be its own parent.")

    def build_feature_tree(self, features_list):
        """Construye un árbol de features a partir de una lista plana."""
        from app.models import FeaturePublicWithChildren

        feature_map = {
            str(f.id): FeaturePublicWithChildren.model_validate(f)
            for f in features_list
        }
        root_features = []

        for feature_public in feature_map.values():
            if feature_public.parent_id:
                parent_id_str = str(feature_public.parent_id)
                if parent_id_str in feature_map:
                    feature_map[parent_id_str].children.append(feature_public)
            else:
                root_features.append(feature_public)

        return root_features


class BaseFeatureRelationRepository:
    """Clase base con lógica compartida para repositorios de relaciones entre features."""

    def validate_features_exist(self, source_feature, target_feature):
        """Valida que las features de origen y destino existen."""
        if not source_feature or not target_feature:
            raise ValueError("Source or target feature not found.")

    def validate_same_version(self, source_feature, target_feature):
        """Valida que ambas features pertenecen a la misma versión del modelo."""
        if (
            source_feature.feature_model_version_id
            != target_feature.feature_model_version_id
        ):
            raise ValueError(
                "Source and target features must belong to the same model version."
            )


class BaseFeatureGroupRepository:
    """Clase base con lógica compartida para repositorios de grupos de features."""

    def validate_parent_feature_exists(self, parent_feature):
        """Valida que la feature padre existe."""
        if not parent_feature:
            raise ValueError("Parent feature not found.")


class BaseConstraintRepository:
    """Clase base con lógica compartida para repositorios de constraints."""

    def validate_feature_model_version_exists(self, version):
        """Valida que la versión del feature model existe."""
        if not version:
            raise ValueError("Source Feature Model Version not found.")


class BaseConfigurationRepository:
    """Clase base con lógica compartida para repositorios de configuraciones."""

    pass  # Por ahora no hay lógica compartida específica, pero la estructura está lista


class BaseFeatureModelVersionRepository:
    """Clase base con lógica compartida para repositorios de versiones de feature models."""

    pass  # Por ahora no hay lógica compartida específica, pero la estructura está lista
