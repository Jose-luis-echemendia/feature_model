import uuid
from fastapi import APIRouter, Depends, HTTPException, status

from app import crud
from app.api.deps import SessionDep, ModelDesignerUser
from app.models.common import Message
from app.models.feature_relation import FeatureRelationCreate, FeatureRelationPublic

router = APIRouter(prefix="/feature-relations", tags=["feature-relations"])


@router.post(
    "/", response_model=FeatureRelationPublic, status_code=status.HTTP_201_CREATED
)
def create_feature_relation(
    *,
    session: SessionDep,
    relation_in: FeatureRelationCreate,
    current_user: ModelDesignerUser,
):
    """
    Create a new feature relation. This will trigger the creation of a new model version.
    Only accessible to Model Designers and Admins.
    """
    # Permisos: Verificamos que el usuario es dueño del modelo al que pertenecen las features.
    # La lógica CRUD se encarga de las validaciones de consistencia.
    source_feature = crud.get_feature(
        session=session, feature_id=relation_in.source_feature_id
    )
    if not source_feature:
        raise HTTPException(status_code=404, detail="Source feature not found.")

    session.refresh(source_feature, ["feature_model_version"])
    session.refresh(source_feature.feature_model_version, ["feature_model"])

    if (
        source_feature.feature_model_version.feature_model.owner_id != current_user.id
        and not current_user.is_superuser
    ):
        raise HTTPException(status_code=403, detail="Not enough permissions.")

    try:
        relation = crud.create_feature_relation(
            session=session, relation_in=relation_in, user=current_user
        )
        return relation
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{relation_id}/", response_model=Message)
def delete_feature_relation(
    *,
    relation_id: uuid.UUID,
    session: SessionDep,
    current_user: ModelDesignerUser,
):
    """
    Delete a feature relation. This will trigger the creation of a new model version.
    """
    db_relation = crud.get_feature_relation(session=session, relation_id=relation_id)
    if not db_relation:
        raise HTTPException(status_code=404, detail="Feature relation not found.")

    session.refresh(db_relation, ["feature_model_version"])
    session.refresh(db_relation.feature_model_version, ["feature_model"])

    if (
        db_relation.feature_model_version.feature_model.owner_id != current_user.id
        and not current_user.is_superuser
    ):
        raise HTTPException(status_code=403, detail="Not enough permissions.")

    crud.delete_feature_relation(
        session=session, db_relation=db_relation, user=current_user
    )
    return Message(
        message="Feature relation deleted in new model version created successfully."
    )
