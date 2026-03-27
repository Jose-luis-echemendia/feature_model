#!/usr/bin/env python3
"""
Script de verificación para S3Service y S3StorageService
Verifica que los servicios estén correctamente configurados.
"""

import asyncio
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.MINIO_storage import S3Service, S3StorageService
from app.core.config import settings


def check_sync_initialization():
    """Verifica la inicialización del servicio síncrono."""
    print("\n" + "=" * 60)
    print("🔍 Verificando S3Service (sync)...")
    print("=" * 60)

    try:
        S3Service.init_sync()
        client = S3Service.get_sync()

        print("✅ Cliente síncrono inicializado correctamente")
        print(f"   Endpoint: {settings.MINIO_ENDPOINT}")
        print(f"   Bucket: {settings.MINIO_BUCKET_NAME}")
        print(f"   SSL: {settings.MINIO_USE_SSL}")

        # Verificar que puede listar el bucket
        response = client.list_objects_v2(Bucket=settings.MINIO_BUCKET_NAME, MaxKeys=1)
        print(f"✅ Conexión al bucket verificada")
        print(f"   Objetos en bucket: {response.get('KeyCount', 0)}")

        return True

    except Exception as e:
        print(f"❌ Error en inicialización síncrona: {e}")
        return False


async def check_async_initialization():
    """Verifica la inicialización del servicio asíncrono."""
    print("\n" + "=" * 60)
    print("🔍 Verificando S3Service (async)...")
    print("=" * 60)

    try:
        await S3Service.init_async()
        session = S3Service.get_async()

        print("✅ Sesión asíncrona inicializada correctamente")
        print(f"   Endpoint: {settings.MINIO_ENDPOINT}")
        print(f"   Bucket: {settings.MINIO_BUCKET_NAME}")
        print(f"   SSL: {settings.MINIO_USE_SSL}")

        # Verificar que puede listar el bucket
        protocol = "https" if settings.MINIO_USE_SSL else "http"
        endpoint_url = f"{protocol}://{settings.MINIO_ENDPOINT}"

        from botocore.client import Config

        async with session.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=settings.MINIO_ACCESS_KEY,
            aws_secret_access_key=settings.MINIO_SECRET_KEY,
            config=Config(signature_version="s3v4"),
        ) as client:
            response = await client.list_objects_v2(
                Bucket=settings.MINIO_BUCKET_NAME, MaxKeys=1
            )
            print(f"✅ Conexión al bucket verificada")
            print(f"   Objetos en bucket: {response.get('KeyCount', 0)}")

        return True

    except Exception as e:
        print(f"❌ Error en inicialización asíncrona: {e}")
        import traceback

        traceback.print_exc()
        return False


def check_storage_service_sync():
    """Verifica S3StorageService en modo síncrono."""
    print("\n" + "=" * 60)
    print("🔍 Verificando S3StorageService (sync)...")
    print("=" * 60)

    try:
        storage = S3StorageService(bucket_name=settings.MINIO_BUCKET_NAME)
        print("✅ S3StorageService inicializado correctamente")
        print(f"   Bucket: {storage.bucket_name}")
        print(f"   Cliente sync: {'✓' if storage.sync_client else '✗'}")
        print(f"   Sesión async: {'✓' if storage.async_session else '✗'}")

        return True

    except Exception as e:
        print(f"❌ Error al inicializar S3StorageService: {e}")
        return False


async def check_storage_service_async():
    """Verifica S3StorageService en modo asíncrono."""
    print("\n" + "=" * 60)
    print("🔍 Verificando métodos asíncronos de S3StorageService...")
    print("=" * 60)

    try:
        storage = S3StorageService(bucket_name=settings.MINIO_BUCKET_NAME)

        # Test file_exists con un archivo que probablemente no existe
        test_object = "verification-test-file-that-does-not-exist.txt"
        exists = await storage.afile_exists(test_object)

        print(f"✅ Método afile_exists funciona correctamente")
        print(f"   Archivo de prueba '{test_object}' existe: {exists}")

        return True

    except Exception as e:
        print(f"❌ Error al verificar métodos asíncronos: {e}")
        import traceback

        traceback.print_exc()
        return False


def print_dependencies():
    """Imprime información sobre las dependencias."""
    print("\n" + "=" * 60)
    print("📦 Verificando dependencias...")
    print("=" * 60)

    try:
        import boto3

        print(f"✅ boto3: {boto3.__version__}")
    except ImportError:
        print("❌ boto3 no instalado")
        return False

    try:
        import aioboto3

        print(f"✅ aioboto3: {aioboto3.__version__}")
    except ImportError:
        print("❌ aioboto3 no instalado - Ejecuta: pip install aioboto3")
        return False

    return True


async def main():
    """Función principal."""
    print("\n" + "=" * 70)
    print("  🧪 VERIFICACIÓN DE S3SERVICE Y S3STORAGESERVICE")
    print("=" * 70)

    # Verificar dependencias
    if not print_dependencies():
        print("\n❌ Faltan dependencias. Por favor instálalas primero.")
        return False

    # Verificar configuración
    print("\n" + "=" * 60)
    print("⚙️  Configuración actual:")
    print("=" * 60)
    print(f"   MINIO_ENDPOINT: {settings.MINIO_ENDPOINT}")
    print(f"   MINIO_BUCKET_NAME: {settings.MINIO_BUCKET_NAME}")
    print(f"   MINIO_USE_SSL: {settings.MINIO_USE_SSL}")
    print(
        f"   MINIO_ACCESS_KEY: {settings.MINIO_ACCESS_KEY[:4]}...{settings.MINIO_ACCESS_KEY[-4:]}"
    )

    # Ejecutar verificaciones
    results = []

    # Sync checks
    results.append(check_sync_initialization())
    results.append(check_storage_service_sync())

    # Async checks
    results.append(await check_async_initialization())
    results.append(await check_storage_service_async())

    # Resumen
    print("\n" + "=" * 70)
    print("📊 RESUMEN")
    print("=" * 70)

    total = len(results)
    passed = sum(results)
    failed = total - passed

    print(f"   Total de verificaciones: {total}")
    print(f"   ✅ Exitosas: {passed}")
    print(f"   ❌ Fallidas: {failed}")

    if all(results):
        print("\n🎉 ¡Todas las verificaciones pasaron exitosamente!")
        print("   Los servicios S3 están listos para usarse.")
        return True
    else:
        print("\n⚠️  Algunas verificaciones fallaron.")
        print("   Revisa los errores arriba y verifica tu configuración.")
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Verificación cancelada por el usuario.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error inesperado: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
