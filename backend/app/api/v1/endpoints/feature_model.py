import uuid

from typing import Optional

from fastapi import APIRouter, Depends
from fastapi_cache.decorator import cache

from app.api.deps import (
    AsyncFeatureModelRepoDep,
    AsyncDomainRepoDep,
    AsyncCurrentUser,
    get_verified_user,
)
from app.exceptions import (
    FeatureModelNotFoundException,
    NotFoundException,
    ForbiddenException,
    BusinessLogicException,
    UnauthorizedException,
)
from app.models.common import Message
from app.models.feature_model import (
    FeatureModelCreate,
    FeatureModelListResponse,
    FeatureModelListItem,
    FeatureModelPublic,
    FeatureModelUpdate,
    VersionInfo,
    LatestVersionInfo,
)

router = APIRouter(
    prefix="/feature-models",
    tags=["Feature Models"],
    responses={
        404: {"description": "Feature model not found"},
        403: {"description": "Not enough permissions"},
        400: {"description": "Validation error"},
    },
)


@router.get(
    "/",
    dependencies=[Depends(get_verified_user)],
    response_model=FeatureModelListResponse,
)
@cache(expire=300)  # Cache por 5 minutos
async def read_feature_models(
    feature_model_repo: AsyncFeatureModelRepoDep,
    skip: int = 0,
    limit: int = 100,
    domain_id: Optional[uuid.UUID] = None,
) -> FeatureModelListResponse:
    """
    Retrieve all feature models with pagination.

    This endpoint returns a paginated list of feature models. Results can be filtered
    by domain and are cached for 5 minutes to improve performance.

    Args:
        feature_model_repo: Feature model repository dependency
        skip: Number of records to skip for pagination (default: 0)
        limit: Maximum number of records to return (default: 100)
        domain_id: Optional UUID to filter models by a specific domain

    Returns:
        FeatureModelListResponse: Paginated list of feature models with metadata
            - data: List of feature models (without description for optimization)
                - id: Feature model UUID
                - name: Feature model name
                - owner_id: Owner user UUID
                - domain_id: Domain UUID
                - domain_name: Name of the associated domain
                - created_at: Creation timestamp
                - updated_at: Last update timestamp
                - is_active: Active status
                - versions_count: Total number of versions
                - latest_version: Information about the latest version
                    - id: Version UUID
                    - version_number: Version number
                    - status: Version status (DRAFT, IN_REVIEW, PUBLISHED)
            - count: Total number of matching records
            - page: Current page number
            - size: Number of items in current page
            - total_pages: Total number of pages
            - has_next: Boolean indicating if there's a next page
            - has_prev: Boolean indicating if there's a previous page

    Raises:
        HTTPException: If domain_id is provided but domain doesn't exist

    Example:
        GET /feature-models/?skip=0&limit=10&domain_id=123e4567-e89b-12d3-a456-426614174000
    """
    if domain_id:
        models = await feature_model_repo.get_by_domain(
            domain_id=domain_id, skip=skip, limit=limit
        )
        count = await feature_model_repo.count(domain_id=domain_id)
    else:
        models = await feature_model_repo.get_all(skip=skip, limit=limit)
        count = await feature_model_repo.count()

    # Convertir a FeatureModelListItem con domain_name y versiones
    list_items = []
    for model in models:
        # Ordenar versiones por version_number descendente
        sorted_versions = sorted(
            model.versions, key=lambda v: v.version_number, reverse=True
        )

        # Obtener la última versión si existe
        latest_version = None
        if sorted_versions:
            latest = sorted_versions[0]
            latest_version = LatestVersionInfo(
                id=latest.id,
                version_number=latest.version_number,
                status=latest.status.value,
            )

        list_items.append(
            FeatureModelListItem(
                id=model.id,
                name=model.name,
                owner_id=model.owner_id,
                domain_id=model.domain_id,
                domain_name=model.domain.name,
                created_at=model.created_at,
                updated_at=model.updated_at,
                is_active=model.is_active,
                versions_count=len(model.versions),
                latest_version=latest_version,
            )
        )

    return FeatureModelListResponse.create(
        data=list_items,
        count=count,
        skip=skip,
        limit=limit,
    )


@router.post(
    "/", response_model=FeatureModelPublic, status_code=status.HTTP_201_CREATED
)
async def create_feature_model(
    *,
    feature_model_repo: AsyncFeatureModelRepoDep,
    domain_repo: AsyncDomainRepoDep,
    model_in: FeatureModelCreate,
    current_user: AsyncCurrentUser,
) -> FeatureModelPublic:
    """
    Create a new feature model.

    This endpoint allows authorized users to create a new feature model within a specific domain.
    The model will be owned by the authenticated user making the request.

    Permissions Required:
        - MODEL_DESIGNER: Can create feature models
        - ADMIN: Can create feature models
        - DEVELOPER: Can create feature models

    Args:
        feature_model_repo: Feature model repository dependency
        domain_repo: Domain repository dependency
        model_in: Feature model creation data (name, description, domain_id)
        current_user: Authenticated user making the request

    Returns:
        FeatureModelPublic: The newly created feature model with all its attributes
            - id: Unique identifier
            - name: Model name
            - description: Model description
            - domain_id: Associated domain ID
            - domain_name: Name of the associated domain
            - owner_id: ID of the user who created the model
            - created_at: Timestamp of creation
            - updated_at: Last update timestamp
            - is_active: Active status (default: true)

    Raises:
        HTTPException 403: If user doesn't have required permissions
        HTTPException 404: If specified domain doesn't exist
        HTTPException 400: If validation fails (e.g., duplicate name in domain)

    Example:
        POST /feature-models/
        {
            "name": "E-commerce Feature Model",
            "description": "Model for e-commerce platform features",
            "domain_id": "123e4567-e89b-12d3-a456-426614174000"
        }
    """
    # Verificar que el usuario tiene permisos (MODEL_DESIGNER o ADMIN)
    from app.enums import UserRole

    if current_user.role not in [
        UserRole.MODEL_DESIGNER,
        UserRole.ADMIN,
        UserRole.DEVELOPER,
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Only Model Designers and Admins can create feature models.",
        )

    # Verificar que el dominio existe
    domain = await domain_repo.get(model_in.domain_id)
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found.")

    try:
        model = await feature_model_repo.create(data=model_in, owner_id=current_user.id)
        # Recargar con domain y versiones
        model_with_domain = await feature_model_repo.get(model.id)

        # Construir lista de versiones
        versions = [
            VersionInfo(
                id=version.id,
                version_number=version.version_number,
                status=version.status.value,
                created_at=version.created_at,
            )
            for version in model_with_domain.versions
        ]

        return FeatureModelPublic(
            id=model_with_domain.id,
            name=model_with_domain.name,
            description=model_with_domain.description,
            owner_id=model_with_domain.owner_id,
            domain_id=model_with_domain.domain_id,
            domain_name=model_with_domain.domain.name,
            created_at=model_with_domain.created_at,
            updated_at=model_with_domain.updated_at,
            is_active=model_with_domain.is_active,
            versions_count=len(model_with_domain.versions),
            versions=versions,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/{model_id}/",
    dependencies=[Depends(get_verified_user)],
    response_model=FeatureModelPublic,
)
@cache(expire=300)  # Cache por 5 minutos
async def read_feature_model(
    *, model_id: uuid.UUID, feature_model_repo: AsyncFeatureModelRepoDep
) -> FeatureModelPublic:
    """
    Retrieve a specific feature model by its ID.

    This endpoint returns detailed information about a single feature model.
    Results are cached for 5 minutes to improve performance.

    Args:
        model_id: UUID of the feature model to retrieve
        feature_model_repo: Feature model repository dependency

    Returns:
        FeatureModelPublic: Complete feature model information including:
            - id: Unique identifier
            - name: Model name
            - description: Model description (included in detail view)
            - domain_id: Associated domain ID
            - domain_name: Name of the associated domain
            - owner_id: ID of the model owner
            - created_at: Creation timestamp
            - updated_at: Last update timestamp
            - is_active: Active status
            - versions_count: Total number of versions
            - versions: List of all versions with details
                - id: Version UUID
                - version_number: Version number
                - status: Version status (DRAFT, IN_REVIEW, PUBLISHED)
                - created_at: Version creation timestamp

    Raises:
        HTTPException 404: If feature model with given ID doesn't exist

    Example:
        GET /feature-models/123e4567-e89b-12d3-a456-426614174000/
    """
    model = await feature_model_repo.get(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Feature Model not found")

    # Ordenar versiones por version_number ascendente
    sorted_versions = sorted(model.versions, key=lambda v: v.version_number)

    # Construir lista de versiones
    versions = [
        VersionInfo(
            id=version.id,
            version_number=version.version_number,
            status=version.status.value,
            created_at=version.created_at,
        )
        for version in sorted_versions
    ]

    # Construir respuesta con domain_name y versiones
    return FeatureModelPublic(
        id=model.id,
        name=model.name,
        description=model.description,
        owner_id=model.owner_id,
        domain_id=model.domain_id,
        domain_name=model.domain.name,
        created_at=model.created_at,
        updated_at=model.updated_at,
        is_active=model.is_active,
        versions_count=len(model.versions),
        versions=versions,
    )


@router.patch("/{model_id}/", response_model=FeatureModelPublic)
async def update_feature_model(
    *,
    model_id: uuid.UUID,
    feature_model_repo: AsyncFeatureModelRepoDep,
    model_in: FeatureModelUpdate,
    current_user: AsyncCurrentUser,
) -> FeatureModelPublic:
    """
    Update an existing feature model.

    This endpoint allows authorized users to modify feature model attributes.
    Only the model owner or administrators can update a feature model.
    Partial updates are supported - only provided fields will be updated.

    Permissions Required:
        - MODEL_DESIGNER: Can update their own models
        - ADMIN: Can update any model
        - DEVELOPER: Can update their own models
        - Model Owner: Can update their own models

    Args:
        model_id: UUID of the feature model to update
        feature_model_repo: Feature model repository dependency
        model_in: Feature model update data (all fields optional)
        current_user: Authenticated user making the request

    Returns:
        FeatureModelPublic: Updated feature model with all current attributes

    Raises:
        HTTPException 403: If user doesn't have permission to update this model
        HTTPException 404: If feature model doesn't exist
        HTTPException 400: If validation fails (e.g., duplicate name in domain)

    Example:
        PATCH /feature-models/123e4567-e89b-12d3-a456-426614174000/
        {
            "name": "Updated Model Name",
            "description": "New description"
        }
    """
    # Verificar que el usuario tiene permisos (MODEL_DESIGNER o ADMIN)
    from app.enums import UserRole

    if current_user.role not in [
        UserRole.MODEL_DESIGNER,
        UserRole.ADMIN,
        UserRole.DEVELOPER,
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Only Model Designers and Admins can update feature models.",
        )

    db_model = await feature_model_repo.get(model_id)
    if not db_model:
        raise HTTPException(status_code=404, detail="Feature Model not found")

    # Verificar si el usuario es el propietario o un admin
    if db_model.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    try:
        updated_model = await feature_model_repo.update(
            db_feature_model=db_model, data=model_in
        )
        # Recargar con domain y versiones
        model_with_domain = await feature_model_repo.get(updated_model.id)

        # Construir lista de versiones
        versions = [
            VersionInfo(
                id=version.id,
                version_number=version.version_number,
                status=version.status.value,
                created_at=version.created_at,
            )
            for version in model_with_domain.versions
        ]

        return FeatureModelPublic(
            id=model_with_domain.id,
            name=model_with_domain.name,
            description=model_with_domain.description,
            owner_id=model_with_domain.owner_id,
            domain_id=model_with_domain.domain_id,
            domain_name=model_with_domain.domain.name,
            created_at=model_with_domain.created_at,
            updated_at=model_with_domain.updated_at,
            is_active=model_with_domain.is_active,
            versions_count=len(model_with_domain.versions),
            versions=versions,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{model_id}/activate/", response_model=FeatureModelPublic)
async def activate_feature_model(
    *,
    model_id: uuid.UUID,
    feature_model_repo: AsyncFeatureModelRepoDep,
    current_user: AsyncCurrentUser,
) -> FeatureModelPublic:
    """
    Activate a feature model.

    This endpoint sets the `is_active` flag to `true`, making the feature model
    active and available for use. Only authorized users can activate models.

    Permissions Required:
        - MODEL_DESIGNER: Can activate their own models
        - ADMIN: Can activate any model
        - DEVELOPER: Can activate their own models
        - Model Owner: Can activate their own models

    Args:
        model_id: UUID of the feature model to activate
        feature_model_repo: Feature model repository dependency
        current_user: Authenticated user making the request

    Returns:
        FeatureModelPublic: Activated feature model with is_active=true

    Raises:
        HTTPException 403: If user doesn't have permission to activate this model
        HTTPException 404: If feature model doesn't exist

    Example:
        PATCH /feature-models/123e4567-e89b-12d3-a456-426614174000/activate/
    """
    # Verificar que el usuario tiene permisos (MODEL_DESIGNER o ADMIN)
    from app.enums import UserRole

    if current_user.role not in [
        UserRole.MODEL_DESIGNER,
        UserRole.ADMIN,
        UserRole.DEVELOPER,
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Only Model Designers and Admins can activate feature models.",
        )

    db_model = await feature_model_repo.get(model_id)
    if not db_model:
        raise HTTPException(status_code=404, detail="Feature Model not found")

    # Verificar si el usuario es el propietario o un admin
    if db_model.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    activated_model = await feature_model_repo.activate(db_model)
    # Recargar con domain y versiones
    model_with_domain = await feature_model_repo.get(activated_model.id)

    # Construir lista de versiones
    versions = [
        VersionInfo(
            id=version.id,
            version_number=version.version_number,
            status=version.status.value,
            created_at=version.created_at,
        )
        for version in model_with_domain.versions
    ]

    return FeatureModelPublic(
        id=model_with_domain.id,
        name=model_with_domain.name,
        description=model_with_domain.description,
        owner_id=model_with_domain.owner_id,
        domain_id=model_with_domain.domain_id,
        domain_name=model_with_domain.domain.name,
        created_at=model_with_domain.created_at,
        updated_at=model_with_domain.updated_at,
        is_active=model_with_domain.is_active,
        versions_count=len(model_with_domain.versions),
        versions=versions,
    )


@router.patch("/{model_id}/deactivate/", response_model=FeatureModelPublic)
async def deactivate_feature_model(
    *,
    model_id: uuid.UUID,
    feature_model_repo: AsyncFeatureModelRepoDep,
    current_user: AsyncCurrentUser,
) -> FeatureModelPublic:
    """
    Deactivate a feature model.

    This endpoint sets the `is_active` flag to `false`, making the feature model
    inactive. Deactivated models are preserved in the database but marked as inactive.
    This is a soft-delete operation that allows reactivation later.

    Permissions Required:
        - MODEL_DESIGNER: Can deactivate their own models
        - ADMIN: Can deactivate any model
        - DEVELOPER: Can deactivate their own models
        - Model Owner: Can deactivate their own models

    Args:
        model_id: UUID of the feature model to deactivate
        feature_model_repo: Feature model repository dependency
        current_user: Authenticated user making the request

    Returns:
        FeatureModelPublic: Deactivated feature model with is_active=false

    Raises:
        HTTPException 403: If user doesn't have permission to deactivate this model
        HTTPException 404: If feature model doesn't exist

    Note:
        Deactivated models can be reactivated using the activate endpoint.
        This operation does not delete any associated data.

    Example:
        PATCH /feature-models/123e4567-e89b-12d3-a456-426614174000/deactivate/
    """
    # Verificar que el usuario tiene permisos (MODEL_DESIGNER o ADMIN)
    from app.enums import UserRole

    if current_user.role not in [
        UserRole.MODEL_DESIGNER,
        UserRole.ADMIN,
        UserRole.DEVELOPER,
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Only Model Designers and Admins can deactivate feature models.",
        )

    db_model = await feature_model_repo.get(model_id)
    if not db_model:
        raise HTTPException(status_code=404, detail="Feature Model not found")

    # Verificar si el usuario es el propietario o un admin
    if db_model.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    deactivated_model = await feature_model_repo.deactivate(db_model)
    # Recargar con domain y versiones
    model_with_domain = await feature_model_repo.get(deactivated_model.id)

    # Construir lista de versiones
    versions = [
        VersionInfo(
            id=version.id,
            version_number=version.version_number,
            status=version.status.value,
            created_at=version.created_at,
        )
        for version in model_with_domain.versions
    ]

    return FeatureModelPublic(
        id=model_with_domain.id,
        name=model_with_domain.name,
        description=model_with_domain.description,
        owner_id=model_with_domain.owner_id,
        domain_id=model_with_domain.domain_id,
        domain_name=model_with_domain.domain.name,
        created_at=model_with_domain.created_at,
        updated_at=model_with_domain.updated_at,
        is_active=model_with_domain.is_active,
        versions_count=len(model_with_domain.versions),
        versions=versions,
    )


@router.delete("/{model_id}/", response_model=Message)
async def delete_feature_model(
    *,
    model_id: uuid.UUID,
    feature_model_repo: AsyncFeatureModelRepoDep,
    current_user: AsyncCurrentUser,
) -> Message:
    """
    Permanently delete a feature model.

    This endpoint performs a hard delete of a feature model from the database.
    **Important:** Deletion is only allowed if the model has NO associated features
    or configurations in any of its versions. If you want to preserve the model
    but mark it as unused, use the deactivate endpoint instead.

    Permissions Required:
        - MODEL_DESIGNER: Can delete their own models
        - ADMIN: Can delete any model
        - DEVELOPER: Can delete their own models
        - Model Owner: Can delete their own models

    Validation Rules:
        - The model must have no features in any version
        - The model must have no configurations in any version
        - Only the owner or admin can delete the model

    Args:
        model_id: UUID of the feature model to delete
        feature_model_repo: Feature model repository dependency
        current_user: Authenticated user making the request

    Returns:
        Message: Success confirmation message

    Raises:
        HTTPException 403: If user doesn't have permission to delete this model
        HTTPException 404: If feature model doesn't exist
        HTTPException 400: If model has associated features or configurations

    Warning:
        This operation is irreversible. Consider using deactivate instead
        if you want to preserve the model for future reference.

    Example:
        DELETE /feature-models/123e4567-e89b-12d3-a456-426614174000/

    Response Example:
        {
            "message": "Feature Model deleted successfully."
        }
    """
    # Verificar que el usuario tiene permisos (MODEL_DESIGNER o ADMIN)
    from app.enums import UserRole

    if current_user.role not in [
        UserRole.MODEL_DESIGNER,
        UserRole.ADMIN,
        UserRole.DEVELOPER,
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Only Model Designers and Admins can delete feature models.",
        )

    db_model = await feature_model_repo.get(model_id)
    if not db_model:
        raise HTTPException(status_code=404, detail="Feature Model not found")

    if db_model.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Verificar que el modelo puede ser eliminado
    can_delete, error_message = await feature_model_repo.can_be_deleted(model_id)
    if not can_delete:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message,
        )

    await feature_model_repo.delete(db_model)
    return Message(message="Feature Model deleted successfully.")
