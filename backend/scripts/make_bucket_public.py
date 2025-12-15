#!/usr/bin/env python3
"""
Script para hacer público el bucket de MinIO.
Ejecutar desde el contenedor backend o localmente con acceso a MinIO.
"""
import boto3
import json
import logging
import sys
from datetime import datetime
from botocore.client import Config
from botocore.exceptions import ClientError

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# Configuración de MinIO
ENDPOINT = "http://localhost:9000"
ACCESS_KEY = "minioadmin"
SECRET_KEY = "minioadminsecret"
BUCKET_NAME = "media"

# Política de bucket pública para lectura
PUBLIC_READ_POLICY = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicRead",
            "Effect": "Allow",
            "Principal": "*",
            "Action": ["s3:GetObject"],
            "Resource": [f"arn:aws:s3:::{BUCKET_NAME}/*"],
        }
    ],
}


def make_bucket_public():
    """Hace público el bucket de MinIO para lectura."""
    logger.info("=" * 60)
    logger.info("🚀 Iniciando script para hacer público el bucket de MinIO")
    logger.info("=" * 60)
    logger.info(f"📅 Timestamp: {datetime.now().isoformat()}")
    logger.info(f"🔗 Endpoint: {ENDPOINT}")
    logger.info(f"🪣 Bucket: {BUCKET_NAME}")
    logger.info(f"🔑 Access Key: {ACCESS_KEY[:4]}***")

    try:
        # Crear cliente S3
        logger.info("🔧 Creando cliente S3...")
        logger.debug(f"Configuración - Endpoint: {ENDPOINT}")
        logger.debug(f"Configuración - Signature version: s3v4")

        client = boto3.client(
            "s3",
            endpoint_url=ENDPOINT,
            aws_access_key_id=ACCESS_KEY,
            aws_secret_access_key=SECRET_KEY,
            config=Config(signature_version="s3v4"),
        )
        logger.info("✅ Cliente S3 creado exitosamente")

        logger.info(f"🔍 Conectando a MinIO en {ENDPOINT}...")

        # Verificar que el bucket existe
        try:
            logger.debug(f"Verificando existencia del bucket '{BUCKET_NAME}'...")
            client.head_bucket(Bucket=BUCKET_NAME)
            logger.info(f"✓ Bucket '{BUCKET_NAME}' encontrado")
            print(f"✓ Bucket '{BUCKET_NAME}' encontrado")
        except ClientError as e:
            error_code = int(e.response["Error"]["Code"])
            logger.warning(f"⚠️ ClientError al verificar bucket: {error_code}")
            logger.debug(f"Detalles del error: {e.response}")

            if error_code == 404:
                logger.info(f"📦 Bucket '{BUCKET_NAME}' no existe. Creándolo...")
                print(f"✗ Bucket '{BUCKET_NAME}' no existe. Creándolo...")

                client.create_bucket(Bucket=BUCKET_NAME)
                logger.info(f"✅ Bucket '{BUCKET_NAME}' creado exitosamente")
                print(f"✓ Bucket '{BUCKET_NAME}' creado")
            else:
                logger.error(f"❌ Error inesperado al verificar bucket: {error_code}")
                raise

        # Aplicar política pública
        logger.info("📝 Preparando política de lectura pública...")
        policy_string = json.dumps(PUBLIC_READ_POLICY, indent=2)
        logger.debug(f"Política a aplicar:\n{policy_string}")

        logger.info(f"🔒 Aplicando política pública al bucket '{BUCKET_NAME}'...")
        client.put_bucket_policy(Bucket=BUCKET_NAME, Policy=policy_string)
        logger.info(f"✅ Política aplicada exitosamente")

        print(f"✓ Política de lectura pública aplicada al bucket '{BUCKET_NAME}'")
        print(f"\n✅ ¡Listo! El bucket '{BUCKET_NAME}' ahora es público para lectura.")
        print(f"\nLas URLs de objetos ahora serán accesibles sin autenticación:")
        print(f"http://localhost:9000/{BUCKET_NAME}/ruta/al/archivo.png")

        logger.info("=" * 60)
        logger.info("✅ Script completado exitosamente")
        logger.info("=" * 60)

    except ClientError as e:
        logger.error(f"❌ Error de cliente S3: {e}")
        logger.error(f"📋 Detalles completos: {e.response}")
        logger.debug(f"Stack trace:", exc_info=True)
        print(f"❌ Error de cliente S3: {e}")
        print(f"Detalles: {e.response}")
        return False
    except Exception as e:
        logger.error(f"❌ Error inesperado: {type(e).__name__}: {e}")
        logger.debug(f"Stack trace:", exc_info=True)
        print(f"❌ Error inesperado: {type(e).__name__}: {e}")
        return False

    return True


if __name__ == "__main__":
    logger.info("🎬 Ejecutando script como programa principal")
    success = make_bucket_public()

    if success:
        logger.info("🎉 Ejecución finalizada con éxito")
        exit(0)
    else:
        logger.error("💥 Ejecución finalizada con errores")
        exit(1)
