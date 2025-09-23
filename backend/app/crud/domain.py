from sqlmodel import Session, select
from uuid import UUID

from app.models import Domain, DomainCreate, DomainUpdate, DomainPublic, DomainPublicWithFeatureModels


def get_domains(*, session: Session, skip: int = 0, limit: int = 100) -> list[Domain]:
    """Obtener lista de dominios con paginación"""
    statement = select(Domain).offset(skip).limit(limit)
    domains = session.exec(statement).all()
    return domains


def get_domain(*, session: Session, domain_id: UUID) -> Domain | None:
    """Obtener un dominio por ID"""
    return session.get(Domain, domain_id)


def get_domain_by_name(*, session: Session, name: str) -> Domain | None:
    """Obtener un dominio por nombre"""
    statement = select(Domain).where(Domain.name == name)
    return session.exec(statement).first()


def create_domain(*, session: Session, domain_create: DomainCreate) -> Domain:
    """Crear un nuevo dominio"""
    # Verificar si ya existe un dominio con el mismo nombre
    existing_domain = get_domain_by_name(session=session, name=domain_create.name)
    if existing_domain:
        raise ValueError(f"Ya existe un dominio con el nombre: {domain_create.name}")
    
    db_obj = Domain.model_validate(domain_create)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_domain(*, session: Session, db_domain: Domain, domain_in: DomainUpdate) -> Domain:
    """Actualizar un dominio existente"""
    # Si se está actualizando el nombre, verificar que no exista otro con el mismo nombre
    if domain_in.name and domain_in.name != db_domain.name:
        existing_domain = get_domain_by_name(session=session, name=domain_in.name)
        if existing_domain and existing_domain.id != db_domain.id:
            raise ValueError(f"Ya existe otro dominio con el nombre: {domain_in.name}")
    
    domain_data = domain_in.model_dump(exclude_unset=True)
    db_domain.sqlmodel_update(domain_data)
    session.add(db_domain)
    session.commit()
    session.refresh(db_domain)
    return db_domain


def delete_domain(*, session: Session, db_domain: Domain) -> Domain:
    """Eliminar un dominio"""
    session.delete(db_domain)
    session.commit()
    return db_domain


def get_domain_with_feature_models(*, session: Session, domain_id: UUID) -> DomainPublicWithFeatureModels | None:
    """Obtener un dominio con sus modelos de características relacionados"""
    domain = session.get(Domain, domain_id)
    if not domain:
        return None
    
    # Cargar las relaciones eager loading
    # SQLModel carga las relaciones automáticamente cuando se acceden
    return DomainPublicWithFeatureModels.model_validate(domain)


def domain_exists(*, session: Session, domain_id: UUID) -> bool:
    """Verificar si un dominio existe"""
    return session.get(Domain, domain_id) is not None


def get_domains_count(*, session: Session) -> int:
    """Obtener el número total de dominios"""
    statement = select(Domain)
    return len(session.exec(statement).all())


def search_domains(*, session: Session, search_term: str, skip: int = 0, limit: int = 100) -> list[Domain]:
    """Buscar dominios por nombre o descripción"""
    statement = select(Domain).where(
        (Domain.name.ilike(f"%{search_term}%")) | 
        (Domain.description.ilike(f"%{search_term}%"))
    ).offset(skip).limit(limit)
    return session.exec(statement).all()