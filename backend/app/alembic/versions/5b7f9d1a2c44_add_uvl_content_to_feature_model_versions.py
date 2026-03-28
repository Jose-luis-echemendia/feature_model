"""add uvl content to feature model versions

Revision ID: 5b7f9d1a2c44
Revises: d8b152111a20
Create Date: 2026-03-27 12:30:00.000000

"""

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes

# revision identifiers, used by Alembic.
revision = "5b7f9d1a2c44"
down_revision = "d8b152111a20"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "feature_model_versions",
        sa.Column("uvl_content", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    )


def downgrade():
    op.drop_column("feature_model_versions", "uvl_content")
