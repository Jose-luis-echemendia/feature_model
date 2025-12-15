#!/usr/bin/env python3
"""
Script de validación para verificar que los schemas de versiones están correctamente definidos.
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

try:
    # Importar los schemas
    from app.models.feature_model import (
        VersionInfo,
        LatestVersionInfo,
        FeatureModelPublic,
        FeatureModelListItem,
    )
    from app.enums import ModelStatus
    from datetime import datetime
    import uuid

    print("✅ Imports exitosos")

    # Validar VersionInfo
    version_info = VersionInfo(
        id=uuid.uuid4(), version_number=1, status="DRAFT", created_at=datetime.now()
    )
    print(
        f"✅ VersionInfo creado: v{version_info.version_number} - {version_info.status}"
    )

    # Validar LatestVersionInfo
    latest_version_info = LatestVersionInfo(
        id=uuid.uuid4(), version_number=2, status="PUBLISHED"
    )
    print(
        f"✅ LatestVersionInfo creado: v{latest_version_info.version_number} - {latest_version_info.status}"
    )

    # Validar FeatureModelListItem
    list_item = FeatureModelListItem(
        id=uuid.uuid4(),
        name="Test Model",
        owner_id=uuid.uuid4(),
        domain_id=uuid.uuid4(),
        domain_name="Test Domain",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        is_active=True,
        versions_count=2,
        latest_version=latest_version_info,
    )
    print(
        f"✅ FeatureModelListItem creado: {list_item.name} con {list_item.versions_count} versiones"
    )

    # Validar FeatureModelPublic
    public_model = FeatureModelPublic(
        id=uuid.uuid4(),
        name="Test Model Public",
        description="Test description",
        owner_id=uuid.uuid4(),
        domain_id=uuid.uuid4(),
        domain_name="Test Domain",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        is_active=True,
        versions_count=3,
        versions=[version_info],
    )
    print(
        f"✅ FeatureModelPublic creado: {public_model.name} con {public_model.versions_count} versiones"
    )

    # Validar serialización a JSON
    list_item_json = list_item.model_dump_json()
    print("✅ Serialización a JSON exitosa")

    print("\n" + "=" * 60)
    print("✅ TODOS LOS TESTS PASARON EXITOSAMENTE")
    print("=" * 60)
    print("\nLos siguientes schemas están correctamente implementados:")
    print("  - VersionInfo (id, version_number, status, created_at)")
    print("  - LatestVersionInfo (id, version_number, status)")
    print("  - FeatureModelListItem (con versions_count y latest_version)")
    print("  - FeatureModelPublic (con versions_count y versions)")

except ImportError as e:
    print(f"❌ Error de importación: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error en validación: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
