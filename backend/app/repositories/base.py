class BaseUserRepository:

    def validate_email_unique(self, existing_user):
        if existing_user:
            raise ValueError("El email ya está registrado.")

    def prepare_password(self, password: str) -> str:
        from app.core.security import get_password_hash

        return get_password_hash(password)


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
        """Valida que una feature no pueda ser su propio padre."""
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
