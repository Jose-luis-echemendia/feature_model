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
