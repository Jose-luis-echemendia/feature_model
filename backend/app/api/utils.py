import uuid
from typing import Union

from fastapi import HTTPException, status


async def resolve_version_id_or_latest(
    version_identifier: Union[str, uuid.UUID],
    feature_model_id: uuid.UUID,
    version_repo,
) -> uuid.UUID:
    """
    Resolve a version identifier that can be either a UUID or the literal 'latest'.

    If 'latest', queries the repository for the last PUBLISHED version for the
    given feature_model_id and returns its UUID. Raises HTTPException(404)
    if no published version exists. If the identifier is a UUID string, it
    will be returned as a UUID object. If invalid, raises HTTPException(422).
    """
    if isinstance(version_identifier, uuid.UUID):
        return version_identifier

    if isinstance(version_identifier, str) and version_identifier.lower() == "latest":
        latest = await version_repo.get_latest_published_version(feature_model_id)
        if not latest:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No published version found for this feature model",
            )
        return latest.id

    # Otherwise try to parse as UUID
    try:
        return uuid.UUID(str(version_identifier))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="version_id must be a valid UUID or the literal 'latest'",
        )
