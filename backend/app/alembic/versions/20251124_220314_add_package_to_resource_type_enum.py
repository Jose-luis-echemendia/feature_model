"""add package to resource type enum

Revision ID: 20251124_220314
Revises: d8b152111a20
Create Date: 2025-11-24 22:03:14.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20251124_220314"
down_revision = "d8b152111a20"
branch_labels = None
depends_on = None


def upgrade():
    """
    Agrega el valor 'PACKAGE' al enum ResourceType.

    PACKAGE representa un conjunto de archivos/recursos agrupados como:
    - Laboratorios prácticos
    - Material complementario
    - Plantillas de proyecto
    - Datasets
    - Código fuente
    - Paquetes de evaluación
    """
    # Para PostgreSQL, necesitamos usar ALTER TYPE ... ADD VALUE
    # Nota: ADD VALUE no puede ejecutarse dentro de un bloque transaccional en PostgreSQL < 12
    # pero Alembic lo maneja correctamente
    op.execute("ALTER TYPE resourcetype ADD VALUE IF NOT EXISTS 'PACKAGE'")


def downgrade():
    """
    Revertir es complejo en PostgreSQL porque no se puede eliminar un valor de un ENUM
    que esté en uso. La estrategia profesional es:

    1. Si NO hay datos usando 'PACKAGE', podríamos recrear el enum
    2. Si hay datos usando 'PACKAGE', la reversión fallaría

    Para producción, se recomienda:
    - NO revertir esta migración si ya hay datos
    - Crear una nueva migración que maneje la transición de datos
    - Documentar que esta migración es irreversible en producción
    """
    # OPCIÓN 1: Migración irreversible (recomendado para producción)
    # raise NotImplementedError("Esta migración no puede revertirse si hay datos usando PACKAGE")

    # OPCIÓN 2: Reversión condicional (solo si no hay datos usando PACKAGE)
    # Verificar si hay recursos usando el valor 'PACKAGE'
    connection = op.get_bind()
    result = connection.execute(
        sa.text("SELECT COUNT(*) FROM resources WHERE type = 'PACKAGE'")
    )
    count = result.scalar()

    if count > 0:
        raise ValueError(
            f"No se puede revertir: hay {count} recurso(s) usando el tipo 'PACKAGE'. "
            "Elimina o migra estos recursos primero."
        )

    # Si no hay datos usando PACKAGE, recreamos el enum sin ese valor
    # ADVERTENCIA: Esto es costoso en producción, úsalo con precaución
    op.execute("ALTER TYPE resourcetype RENAME TO resourcetype_old")
    op.execute(
        """
        CREATE TYPE resourcetype AS ENUM (
            'VIDEO',
            'PDF', 
            'QUIZ',
            'EXTERNAL_LINK',
            'TEXT_CONTENT'
        )
    """
    )
    op.execute(
        "ALTER TABLE resources ALTER COLUMN type TYPE resourcetype USING type::text::resourcetype"
    )
    op.execute("DROP TYPE resourcetype_old")
