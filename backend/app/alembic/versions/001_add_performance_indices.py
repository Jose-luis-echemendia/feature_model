"""Add performance indices for feature models

Revision ID: 001_performance_indices
Revises: 5b7f9d1a2c44
Create Date: 2026-05-01 10:00:00.000000

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "001_performance_indices"
down_revision = "5b7f9d1a2c44"
branch_labels = None
depends_on = None


def upgrade():
    """Create indices to optimize common queries for feature models."""

    # ── Índices en tabla `features` ────────────────────────────────────────────
    # Feature model version lookup (usado en tree builder)
    op.create_index(
        "idx_feature_version_id",
        "features",
        ["feature_model_version_id"],
        if_not_exists=True,
    )

    # Parent feature lookup (jerarquía padre-hijo)
    op.create_index(
        "idx_feature_parent_id",
        "features",
        ["parent_id"],
        if_not_exists=True,
    )

    # Group lookup (features por grupo)
    op.create_index(
        "idx_feature_group_id",
        "features",
        ["group_id"],
        if_not_exists=True,
    )

    # ── Índices en tabla `constraints` ─────────────────────────────────────────
    # Constraints por versión (validación/análisis)
    op.create_index(
        "idx_constraint_version_id",
        "constraints",
        ["feature_model_version_id"],
        if_not_exists=True,
    )

    # ── Índices en tabla `feature_relations` ───────────────────────────────────
    # Relations por versión (análisis estructural)
    op.create_index(
        "idx_feature_relation_version_id",
        "feature_relations",
        ["feature_model_version_id"],
        if_not_exists=True,
    )

    # Relations por feature source
    op.create_index(
        "idx_feature_relation_source_id",
        "feature_relations",
        ["source_feature_id"],
        if_not_exists=True,
    )

    # Relations por feature target
    op.create_index(
        "idx_feature_relation_target_id",
        "feature_relations",
        ["target_feature_id"],
        if_not_exists=True,
    )

    # ── Índices en tabla `feature_model_versions` ──────────────────────────────
    # Lookup rápido de versión PUBLISHED
    op.create_index(
        "idx_fm_version_status_model_id",
        "feature_model_versions",
        ["feature_model_id", "status"],
        if_not_exists=True,
    )

    # Ordenamiento por version_number
    op.create_index(
        "idx_fm_version_number_model_id",
        "feature_model_versions",
        ["feature_model_id", "version_number"],
        if_not_exists=True,
    )

    # ── Índices en tabla `feature_model` ───────────────────────────────────────
    # Lookup por owner y domain (listados)
    op.create_index(
        "idx_fm_owner_domain",
        "feature_model",
        ["owner_id", "domain_id"],
        if_not_exists=True,
    )

    # ── Índices en tabla `feature_groups` ──────────────────────────────────────
    # Lookup por parent feature (jerarquía)
    op.create_index(
        "idx_feature_group_parent_feature_id",
        "feature_groups",
        ["parent_feature_id"],
        if_not_exists=True,
    )

    # Lookup por versión
    op.create_index(
        "idx_feature_group_version_id",
        "feature_groups",
        ["feature_model_version_id"],
        if_not_exists=True,
    )

    # ── Índices en tabla `configurations` ──────────────────────────────────────
    # Lookup por versión (para generación de configuraciones)
    op.create_index(
        "idx_configuration_version_id",
        "configurations",
        ["feature_model_version_id"],
        if_not_exists=True,
    )


def downgrade():
    """Remove indices."""

    # Drop feature indices
    op.drop_index("idx_feature_version_id", if_exists=True)
    op.drop_index("idx_feature_parent_id", if_exists=True)
    op.drop_index("idx_feature_group_id", if_exists=True)

    # Drop constraint indices
    op.drop_index("idx_constraint_version_id", if_exists=True)

    # Drop relation indices
    op.drop_index("idx_feature_relation_version_id", if_exists=True)
    op.drop_index("idx_feature_relation_source_id", if_exists=True)
    op.drop_index("idx_feature_relation_target_id", if_exists=True)

    # Drop version indices
    op.drop_index("idx_fm_version_status_model_id", if_exists=True)
    op.drop_index("idx_fm_version_number_model_id", if_exists=True)

    # Drop feature model indices
    op.drop_index("idx_fm_owner_domain", if_exists=True)

    # Drop feature group indices
    op.drop_index("idx_feature_group_parent_feature_id", if_exists=True)
    op.drop_index("idx_feature_group_version_id", if_exists=True)

    # Drop configuration indices
    op.drop_index("idx_configuration_version_id", if_exists=True)
