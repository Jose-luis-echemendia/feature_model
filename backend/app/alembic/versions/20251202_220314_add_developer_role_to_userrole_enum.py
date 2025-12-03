"""add_developer_role_to_userrole_enum

Revision ID: 5e9f91785444
Revises:
Create Date: 2025-11-27 18:58:16.468031

"""

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = "20251202_220314"
down_revision = "20251124_220314"
branch_labels = None
depends_on = None


def upgrade():
    """
    Agrega el valor 'DEVELOPER' al enum UserRole.

    PostgreSQL no permite agregar valores a un enum directamente en una transacción,
    por lo que usamos COMMIT para ejecutar el comando inmediatamente.
    """
    # Agregar el nuevo valor 'DEVELOPER' al enum userrole
    # Usamos IF NOT EXISTS para que sea idempotente
    op.execute("ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'DEVELOPER'")


def downgrade():
    """
    Nota: PostgreSQL no soporta eliminar valores de un enum.

    Para hacer downgrade, necesitarías:
    1. Crear un nuevo enum sin 'developer'
    2. Actualizar todas las columnas que usan el enum
    3. Eliminar el enum viejo
    4. Renombrar el nuevo enum

    Por simplicidad, este downgrade no hace nada ya que eliminar el valor
    'developer' requeriría primero asegurarse de que ningún usuario lo use.
    """
    # No podemos eliminar valores de un enum en PostgreSQL de forma segura
    # sin recrear todo el tipo y actualizar todas las referencias
    pass
