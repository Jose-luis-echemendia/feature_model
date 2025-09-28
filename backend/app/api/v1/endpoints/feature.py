import uuid
from fastapi import APIRouter, Depends, HTTPException, status

from app import crud
from app.api.deps import SessionDep, ModelDesignerUser, VerifiedUser
from app.models.common import Message
from app.models.feature import FeatureCreate, FeaturePublic, FeatureUpdate

router = APIRouter(prefix="/features", tags=["features"])


@router.get(
    "/", dependencies=[Depends(VerifiedUser)], response_model=list[FeaturePublic]
)
def read_features_by_model(
    *,
    session: SessionDep,
    feature_model_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
) -> list[FeaturePublic]:
    """
    Retrieve all features for a specific feature model, structured as a tree.
    """
    features_list = crud.get_features_by_model(
        session=session, feature_model_id=feature_model_id, skip=skip, limit=limit
    )

    # Construir la estructura de árbol
    feature_map = {str(f.id): FeaturePublic.model_validate(f) for f in features_list}
    root_features = []

    for feature in features_list:
        feature_public = feature_map[str(feature.id)]
        if feature.parent_id:
            parent_id_str = str(feature.parent_id)
            if parent_id_str in feature_map:
                feature_map[parent_id_str].children.append(feature_public)
        else:
            root_features.append(feature_public)

    return root_features
