"""initial schema

Revision ID: d8b152111a20
Revises:
Create Date: 2025-11-23 08:06:46.101577

"""

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "d8b152111a20"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # --- NIVEL 1: Tablas sin dependencias externas ---
    # APP SETTINGS
    op.create_table(
        "app_settings",
        sa.Column("key", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column("value", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "description", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True
        ),
        sa.PrimaryKeyConstraint("key"),
    )

    # USERS (con auto-referencias)
    op.create_table(
        "users",
        sa.Column(
            "email", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False
        ),
        sa.Column("is_superuser", sa.Boolean(), nullable=False),
        sa.Column(
            "role",
            sa.Enum(
                "ADMIN",
                "MODEL_DESIGNER",
                "MODEL_EDITOR",
                "CONFIGURATOR",
                "VIEWER",
                "REVIEWER",
                name="userrole",
            ),
            nullable=False,
        ),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_by_id", sa.Uuid(), nullable=True),
        sa.Column("updated_by_id", sa.Uuid(), nullable=True),
        sa.Column("deleted_by_id", sa.Uuid(), nullable=True),
        sa.Column(
            "hashed_password", sqlmodel.sql.sqltypes.AutoString(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["created_by_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["deleted_by_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["updated_by_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_is_active"), "users", ["is_active"], unique=False)

    # --- NIVEL 2: Tablas que dependen solo de users ---
    # DOMAINS
    op.create_table(
        "domains",
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_by_id", sa.Uuid(), nullable=True),
        sa.Column("updated_by_id", sa.Uuid(), nullable=True),
        sa.Column("deleted_by_id", sa.Uuid(), nullable=True),
        sa.ForeignKeyConstraint(
            ["created_by_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["deleted_by_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["updated_by_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_domains_is_active"), "domains", ["is_active"], unique=False
    )
    op.create_index(op.f("ix_domains_name"), "domains", ["name"], unique=False)

    # RESOURCES
    op.create_table(
        "resources",
        sa.Column(
            "title", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False
        ),
        sa.Column(
            "type",
            sa.Enum(
                "VIDEO",
                "PDF",
                "QUIZ",
                "EXTERNAL_LINK",
                "TEXT_CONTENT",
                name="resourcetype",
            ),
            nullable=False,
        ),
        sa.Column(
            "content_url_or_data",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column(
            "language", sqlmodel.sql.sqltypes.AutoString(length=10), nullable=False
        ),
        sa.Column("duration_minutes", sa.Integer(), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "DRAFT", "IN_REVIEW", "PUBLISHED", "ARCHIVED", name="resourcestatus"
            ),
            nullable=False,
        ),
        sa.Column("publication_date", sa.Date(), nullable=True),
        sa.Column("author_name", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("owner_id", sa.Uuid(), nullable=True),
        sa.Column(
            "license",
            sa.Enum(
                "COPYRIGHT",
                "CREATIVE_COMMONS_BY",
                "CREATIVE_COMMONS_BY_SA",
                "PUBLIC_DOMAIN",
                "INTERNAL_USE",
                name="licensetype",
            ),
            nullable=False,
        ),
        sa.Column("valid_until", sa.Date(), nullable=True),
        sa.Column("tags", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "accessibility_notes", sqlmodel.sql.sqltypes.AutoString(), nullable=True
        ),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_by_id", sa.Uuid(), nullable=True),
        sa.Column("updated_by_id", sa.Uuid(), nullable=True),
        sa.Column("deleted_by_id", sa.Uuid(), nullable=True),
        sa.ForeignKeyConstraint(
            ["created_by_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["deleted_by_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["updated_by_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_resources_is_active"), "resources", ["is_active"], unique=False
    )
    op.create_index(op.f("ix_resources_title"), "resources", ["title"], unique=False)

    # TAGS
    op.create_table(
        "tags",
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_by_id", sa.Uuid(), nullable=True),
        sa.Column("updated_by_id", sa.Uuid(), nullable=True),
        sa.Column("deleted_by_id", sa.Uuid(), nullable=True),
        sa.ForeignKeyConstraint(
            ["created_by_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["deleted_by_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["updated_by_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_tags_is_active"), "tags", ["is_active"], unique=False)
    op.create_index(op.f("ix_tags_name"), "tags", ["name"], unique=True)

    # --- NIVEL 3: FEATURE_MODEL (depende de domains y users) ---
    op.create_table(
        "feature_model",
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column(
            "description", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True
        ),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_by_id", sa.Uuid(), nullable=True),
        sa.Column("updated_by_id", sa.Uuid(), nullable=True),
        sa.Column("deleted_by_id", sa.Uuid(), nullable=True),
        sa.Column("domain_id", sa.Uuid(), nullable=False),
        sa.Column("owner_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["created_by_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["deleted_by_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["domain_id"],
            ["domains.id"],
        ),
        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["updated_by_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_feature_model_is_active"), "feature_model", ["is_active"], unique=False
    )
    op.create_index(
        op.f("ix_feature_model_name"), "feature_model", ["name"], unique=False
    )

    # --- NIVEL 4: Tablas que dependen de feature_model ---
    # FEATURE_MODEL_COLLABORATORS
    op.create_table(
        "feature_model_collaborators",
        sa.Column("feature_model_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["feature_model_id"],
            ["feature_model.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("feature_model_id", "user_id"),
    )

    # FEATURE_MODEL_VERSIONS
    op.create_table(
        "feature_model_versions",
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("snapshot", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("feature_model_id", sa.Uuid(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("DRAFT", "IN_REVIEW", "PUBLISHED", "ARCHIVED", name="modelstatus"),
            nullable=False,
        ),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_by_id", sa.Uuid(), nullable=True),
        sa.Column("updated_by_id", sa.Uuid(), nullable=True),
        sa.Column("deleted_by_id", sa.Uuid(), nullable=True),
        sa.ForeignKeyConstraint(
            ["created_by_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["deleted_by_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["feature_model_id"],
            ["feature_model.id"],
        ),
        sa.ForeignKeyConstraint(
            ["updated_by_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_feature_model_versions_is_active"),
        "feature_model_versions",
        ["is_active"],
        unique=False,
    )
    op.create_index(
        op.f("ix_feature_model_versions_version_number"),
        "feature_model_versions",
        ["version_number"],
        unique=False,
    )

    # --- NIVEL 5: FEATURES (depende de feature_model_versions y resources, con auto-referencias) ---
    # NOTA: No incluimos la FK a feature_groups aquí porque aún no existe (dependencia circular)
    # Se agregará después de crear feature_groups
    op.create_table(
        "features",
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column(
            "type", sa.Enum("MANDATORY", "OPTIONAL", name="featuretype"), nullable=False
        ),
        sa.Column("properties", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("feature_model_version_id", sa.Uuid(), nullable=False),
        sa.Column("parent_id", sa.Uuid(), nullable=True),
        sa.Column("group_id", sa.Uuid(), nullable=True),
        sa.Column("resource_id", sa.Uuid(), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_by_id", sa.Uuid(), nullable=True),
        sa.Column("updated_by_id", sa.Uuid(), nullable=True),
        sa.Column("deleted_by_id", sa.Uuid(), nullable=True),
        sa.ForeignKeyConstraint(
            ["created_by_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["deleted_by_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["feature_model_version_id"],
            ["feature_model_versions.id"],
        ),
        # FK a group_id se agregará después de crear feature_groups
        sa.ForeignKeyConstraint(
            ["parent_id"],
            ["features.id"],
        ),
        sa.ForeignKeyConstraint(
            ["resource_id"],
            ["resources.id"],
        ),
        sa.ForeignKeyConstraint(
            ["updated_by_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "feature_model_version_id", "name", name="uq_feature_version_name"
        ),
    )
    op.create_index(
        op.f("ix_features_feature_model_version_id"),
        "features",
        ["feature_model_version_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_features_is_active"), "features", ["is_active"], unique=False
    )
    op.create_index(
        "ix_features_properties_gin",
        "features",
        ["properties"],
        unique=False,
        postgresql_using="gin",
    )

    # --- NIVEL 6: FEATURE_GROUPS (depende de features y feature_model_versions) ---
    op.create_table(
        "feature_groups",
        sa.Column(
            "group_type",
            sa.Enum("ALTERNATIVE", "OR", name="featuregrouptype"),
            nullable=False,
        ),
        sa.Column("min_cardinality", sa.Integer(), nullable=False),
        sa.Column("max_cardinality", sa.Integer(), nullable=True),
        sa.Column("parent_feature_id", sa.Uuid(), nullable=False),
        sa.Column("feature_model_version_id", sa.Uuid(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_by_id", sa.Uuid(), nullable=True),
        sa.Column("updated_by_id", sa.Uuid(), nullable=True),
        sa.Column("deleted_by_id", sa.Uuid(), nullable=True),
        sa.ForeignKeyConstraint(
            ["created_by_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["deleted_by_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["feature_model_version_id"],
            ["feature_model_versions.id"],
        ),
        sa.ForeignKeyConstraint(
            ["parent_feature_id"],
            ["features.id"],
        ),
        sa.ForeignKeyConstraint(
            ["updated_by_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_feature_groups_group_type"),
        "feature_groups",
        ["group_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_feature_groups_is_active"),
        "feature_groups",
        ["is_active"],
        unique=False,
    )

    # Ahora que feature_groups existe, agregamos la FK desde features.group_id
    op.create_foreign_key(
        "fk_features_group_id_feature_groups",
        "features",
        "feature_groups",
        ["group_id"],
        ["id"],
    )

    # --- NIVEL 7: Tablas de relación que dependen de features ---
    # FEATURE_TAGS
    op.create_table(
        "feature_tags",
        sa.Column("feature_id", sa.Uuid(), nullable=False),
        sa.Column("tag_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["feature_id"],
            ["features.id"],
        ),
        sa.ForeignKeyConstraint(
            ["tag_id"],
            ["tags.id"],
        ),
        sa.PrimaryKeyConstraint("feature_id", "tag_id"),
    )

    # FEATURE_RELATIONS
    op.create_table(
        "feature_relations",
        sa.Column(
            "type",
            sa.Enum("REQUIRED", "EXCLUDES", name="featurerelationtype"),
            nullable=False,
        ),
        sa.Column("source_feature_id", sa.Uuid(), nullable=False),
        sa.Column("target_feature_id", sa.Uuid(), nullable=False),
        sa.Column("feature_model_version_id", sa.Uuid(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_by_id", sa.Uuid(), nullable=True),
        sa.Column("updated_by_id", sa.Uuid(), nullable=True),
        sa.Column("deleted_by_id", sa.Uuid(), nullable=True),
        sa.ForeignKeyConstraint(
            ["created_by_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["deleted_by_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["feature_model_version_id"],
            ["feature_model_versions.id"],
        ),
        sa.ForeignKeyConstraint(
            ["source_feature_id"],
            ["features.id"],
        ),
        sa.ForeignKeyConstraint(
            ["target_feature_id"],
            ["features.id"],
        ),
        sa.ForeignKeyConstraint(
            ["updated_by_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_feature_relations_is_active"),
        "feature_relations",
        ["is_active"],
        unique=False,
    )
    op.create_index(
        op.f("ix_feature_relations_source_feature_id"),
        "feature_relations",
        ["source_feature_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_feature_relations_target_feature_id"),
        "feature_relations",
        ["target_feature_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_feature_relations_type"), "feature_relations", ["type"], unique=False
    )

    # --- NIVEL 8: Tablas que dependen de feature_model_versions ---
    # CONFIGURATIONS
    op.create_table(
        "configurations",
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("feature_model_version_id", sa.Uuid(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_by_id", sa.Uuid(), nullable=True),
        sa.Column("updated_by_id", sa.Uuid(), nullable=True),
        sa.Column("deleted_by_id", sa.Uuid(), nullable=True),
        sa.ForeignKeyConstraint(
            ["created_by_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["deleted_by_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["feature_model_version_id"],
            ["feature_model_versions.id"],
        ),
        sa.ForeignKeyConstraint(
            ["updated_by_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_configurations_feature_model_version_id"),
        "configurations",
        ["feature_model_version_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_configurations_is_active"),
        "configurations",
        ["is_active"],
        unique=False,
    )

    # CONSTRAINTS
    op.create_table(
        "constraints",
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("expr_text", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("expr_cnf", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("feature_model_version_id", sa.Uuid(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_by_id", sa.Uuid(), nullable=True),
        sa.Column("updated_by_id", sa.Uuid(), nullable=True),
        sa.Column("deleted_by_id", sa.Uuid(), nullable=True),
        sa.ForeignKeyConstraint(
            ["created_by_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["deleted_by_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["feature_model_version_id"],
            ["feature_model_versions.id"],
        ),
        sa.ForeignKeyConstraint(
            ["updated_by_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_constraints_is_active"), "constraints", ["is_active"], unique=False
    )

    # --- NIVEL 9: Tablas de relación que dependen de configurations ---
    # CONFIGURATION_FEATURES
    op.create_table(
        "configuration_features",
        sa.Column("configuration_id", sa.Uuid(), nullable=False),
        sa.Column("feature_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["configuration_id"],
            ["configurations.id"],
        ),
        sa.ForeignKeyConstraint(
            ["feature_id"],
            ["features.id"],
        ),
        sa.PrimaryKeyConstraint("configuration_id", "feature_id"),
    )
    op.create_table(
        "configuration_tags",
        sa.Column("configuration_id", sa.Uuid(), nullable=False),
        sa.Column("tag_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["configuration_id"],
            ["configurations.id"],
        ),
        sa.ForeignKeyConstraint(
            ["tag_id"],
            ["tags.id"],
        ),
        sa.PrimaryKeyConstraint("configuration_id", "tag_id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # Orden inverso al upgrade - eliminar de las más dependientes a las menos dependientes

    # NIVEL 9: Tablas de relación de configurations
    op.drop_table("configuration_tags")
    op.drop_table("configuration_features")

    # NIVEL 8: Tablas que dependen de feature_model_versions
    op.drop_index(op.f("ix_constraints_is_active"), table_name="constraints")
    op.drop_table("constraints")
    op.drop_index(op.f("ix_configurations_is_active"), table_name="configurations")
    op.drop_index(
        op.f("ix_configurations_feature_model_version_id"), table_name="configurations"
    )
    op.drop_table("configurations")

    # NIVEL 7: Relaciones de features
    op.drop_index(op.f("ix_feature_relations_type"), table_name="feature_relations")
    op.drop_index(
        op.f("ix_feature_relations_target_feature_id"), table_name="feature_relations"
    )
    op.drop_index(
        op.f("ix_feature_relations_source_feature_id"), table_name="feature_relations"
    )
    op.drop_index(
        op.f("ix_feature_relations_is_active"), table_name="feature_relations"
    )
    op.drop_table("feature_relations")
    op.drop_table("feature_tags")

    # NIVEL 6: feature_groups
    # Primero eliminamos la FK desde features.group_id antes de eliminar feature_groups
    op.drop_constraint(
        "fk_features_group_id_feature_groups", "features", type_="foreignkey"
    )
    op.drop_index(op.f("ix_feature_groups_is_active"), table_name="feature_groups")
    op.drop_index(op.f("ix_feature_groups_group_type"), table_name="feature_groups")
    op.drop_table("feature_groups")

    # NIVEL 5: features
    op.drop_index(
        "ix_features_properties_gin", table_name="features", postgresql_using="gin"
    )
    op.drop_index(op.f("ix_features_is_active"), table_name="features")
    op.drop_index(op.f("ix_features_feature_model_version_id"), table_name="features")
    op.drop_table("features")

    # NIVEL 4: Tablas que dependen de feature_model
    op.drop_index(
        op.f("ix_feature_model_versions_version_number"),
        table_name="feature_model_versions",
    )
    op.drop_index(
        op.f("ix_feature_model_versions_is_active"), table_name="feature_model_versions"
    )
    op.drop_table("feature_model_versions")
    op.drop_table("feature_model_collaborators")

    # NIVEL 3: feature_model
    op.drop_index(op.f("ix_feature_model_name"), table_name="feature_model")
    op.drop_index(op.f("ix_feature_model_is_active"), table_name="feature_model")
    op.drop_table("feature_model")

    # NIVEL 2: Tablas que dependen solo de users
    op.drop_index(op.f("ix_tags_name"), table_name="tags")
    op.drop_index(op.f("ix_tags_is_active"), table_name="tags")
    op.drop_table("tags")
    op.drop_index(op.f("ix_resources_title"), table_name="resources")
    op.drop_index(op.f("ix_resources_is_active"), table_name="resources")
    op.drop_table("resources")
    op.drop_index(op.f("ix_domains_name"), table_name="domains")
    op.drop_index(op.f("ix_domains_is_active"), table_name="domains")
    op.drop_table("domains")

    # NIVEL 1: Tablas base
    op.drop_index(op.f("ix_users_is_active"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
    op.drop_table("app_settings")
    # ### end Alembic commands ###
