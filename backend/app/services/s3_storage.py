import uuid, logging, sys, boto3, logging
from pathlib import Path
from typing import Optional
from fastapi import UploadFile, HTTPException, status
from botocore.exceptions import ClientError
from botocore.client import Config
import aioboto3

from app.core.config import settings

logger = logging.getLogger(__name__)


class S3Service:
    """
    Servicio unificado para la conexión con el almacenamiento S3 (Minio).
    Gestiona la inicialización del cliente tanto síncrono como asíncrono.
    Provee acceso tanto asíncrono como sincrónico.
    """

    _sync_client = None
    _async_session: Optional[aioboto3.Session] = None

    @classmethod
    def init_sync(cls) -> None:
        """
        Inicializa el cliente boto3 síncrono, verifica la conexión y asegura que el bucket exista.
        Se debe llamar en el evento startup de FastAPI.
        """
        if cls._sync_client:
            logger.info("El cliente S3 síncrono ya está inicializado.")
            return

        try:
            logger.info("Inicializando cliente S3 síncrono para Minio...")
            protocol = "https" if settings.S3_USE_SSL else "http"
            endpoint_url = f"{protocol}://{settings.S3_ENDPOINT}"

            client = boto3.client(
                "s3",
                endpoint_url=endpoint_url,
                aws_access_key_id=settings.S3_ACCESS_KEY,
                aws_secret_access_key=settings.S3_SECRET_KEY,
                config=Config(signature_version="s3v4"),
            )

            # --- Verificación del Bucket ---
            cls._ensure_bucket_exists_sync(client, settings.S3_BUCKET_NAME)

            # Si todo sale bien, asignamos el cliente
            cls._sync_client = client
            logger.info(
                "✅ S3Service (sync) conectado y bucket verificado exitosamente."
            )

        except ClientError as e:
            logger.critical(
                f"❌ FALLO CRÍTICO: No se pudo conectar a Minio (sync) o verificar el bucket: {e}"
            )
            logger.critical(
                "La aplicación no se iniciará. Revisa la configuración de S3/Minio y la conectividad."
            )
            sys.exit(1)
        except Exception as e:
            logger.critical(
                f"❌ Ocurrió un error inesperado al inicializar S3Service (sync): {e}"
            )
            sys.exit(1)

    @classmethod
    async def init_async(cls) -> None:
        """
        Inicializa el cliente aioboto3 asíncrono y verifica que el bucket exista.
        Se debe llamar en el evento startup de FastAPI.
        """
        if cls._async_session:
            logger.info("El cliente S3 asíncrono ya está inicializado.")
            return

        try:
            logger.info("Inicializando cliente S3 asíncrono para Minio...")
            protocol = "https" if settings.S3_USE_SSL else "http"
            endpoint_url = f"{protocol}://{settings.S3_ENDPOINT}"

            # Crear sesión aioboto3
            session = aioboto3.Session()
            cls._async_session = session

            # Verificar el bucket con cliente temporal
            async with session.client(
                "s3",
                endpoint_url=endpoint_url,
                aws_access_key_id=settings.S3_ACCESS_KEY,
                aws_secret_access_key=settings.S3_SECRET_KEY,
                config=Config(signature_version="s3v4"),
            ) as client:
                await cls._ensure_bucket_exists_async(client, settings.S3_BUCKET_NAME)

            logger.info(
                "✅ S3Service (async) conectado y bucket verificado exitosamente."
            )

        except ClientError as e:
            logger.critical(
                f"❌ FALLO CRÍTICO: No se pudo conectar a Minio (async) o verificar el bucket: {e}"
            )
            logger.critical(
                "La aplicación no se iniciará. Revisa la configuración de S3/Minio y la conectividad."
            )
            sys.exit(1)
        except Exception as e:
            logger.critical(
                f"❌ Ocurrió un error inesperado al inicializar S3Service (async): {e}"
            )
            sys.exit(1)

    @staticmethod
    def _ensure_bucket_exists_sync(client, bucket_name: str) -> None:
        """Método estático para verificar y/o crear el bucket (síncrono)."""
        try:
            client.head_bucket(Bucket=bucket_name)
            logger.info(f"El bucket S3 '{bucket_name}' ya existe (sync).")
        except ClientError as e:
            error_code = int(e.response["Error"]["Code"])
            if error_code == 404:
                logger.warning(
                    f"El bucket S3 '{bucket_name}' no existe. Intentando crear... (sync)"
                )
                client.create_bucket(Bucket=bucket_name)
                logger.info(f"Bucket S3 '{bucket_name}' creado exitosamente (sync).")
            else:
                raise

    @staticmethod
    async def _ensure_bucket_exists_async(client, bucket_name: str) -> None:
        """Método estático para verificar y/o crear el bucket (asíncrono)."""
        try:
            await client.head_bucket(Bucket=bucket_name)
            logger.info(f"El bucket S3 '{bucket_name}' ya existe (async).")
        except ClientError as e:
            error_code = int(e.response["Error"]["Code"])
            if error_code == 404:
                logger.warning(
                    f"El bucket S3 '{bucket_name}' no existe. Intentando crear... (async)"
                )
                await client.create_bucket(Bucket=bucket_name)
                logger.info(f"Bucket S3 '{bucket_name}' creado exitosamente (async).")
            else:
                raise

    @classmethod
    def get_sync(cls):
        """Devuelve la instancia del cliente S3 síncrono inicializado."""
        if cls._sync_client is None:
            logger.error(
                "Se intentó obtener el cliente S3 síncrono antes de su inicialización."
            )
            raise RuntimeError(
                "S3Service (sync) no ha sido inicializado. Llama a S3Service.init_sync() en el startup."
            )
        return cls._sync_client

    @classmethod
    def get_async(cls) -> Optional[aioboto3.Session]:
        """Devuelve la sesión aioboto3 para crear clientes asíncronos."""
        if cls._async_session is None:
            logger.error(
                "Se intentó obtener la sesión S3 asíncrona antes de su inicialización."
            )
            raise RuntimeError(
                "S3Service (async) no ha sido inicializado. Llama a S3Service.init_async() en el startup."
            )
        return cls._async_session


class S3StorageService:
    """
    Servicio para gestionar el almacenamiento de archivos en un bucket S3-compatible (Minio).
    Compatible con uso síncrono y asíncrono.
    """

    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name
        self.sync_client = S3Service.get_sync()
        self.async_session = S3Service.get_async()
        logger.debug(
            "S3StorageService inicializado. bucket='%s', sync_client=%s, async_session=%s",
            bucket_name,
            "disponible" if self.sync_client else "None",
            "disponible" if self.async_session else "None",
        )

    # ==========================================================
    # 🧩 MÉTODOS SINCRÓNICOS
    # ==========================================================

    def save_audio_file(self, file: UploadFile) -> str:
        """
        Guarda un archivo de audio en S3 (modo síncrono).
        """
        try:
            logger.info(
                f"Subiendo archivo '{file.filename}' al bucket S3 '{self.bucket_name}' (sync)..."
            )
            file_extension = Path(file.filename).suffix
            object_name = f"{uuid.uuid4()}{file_extension}"
            logger.debug(f"Nombre de objeto único generado: {object_name}")

            file.file.seek(0)
            self.sync_client.upload_fileobj(
                file.file,
                self.bucket_name,
                object_name,
                ExtraArgs={"ContentType": file.content_type},
            )

            logger.info(
                f"Archivo subido exitosamente a S3 como '{object_name}' (sync)."
            )
            return object_name
        except ClientError as e:
            logger.error(f"Error al subir el archivo a S3 (sync): {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"No se pudo guardar el archivo en el almacenamiento: {e}",
            )
        finally:
            logger.debug(f"Cerrando el archivo de subida '{file.filename}'.")
            file.close()

    def save_file(
        self, file: UploadFile, prefix: str = "", expires_in: int = 3600 * 24 * 7
    ) -> str:
        """
        Guarda un archivo genérico en S3 con un prefijo opcional y retorna una URL presigned (modo síncrono).

        Args:
            file: Archivo a subir
            prefix: Prefijo para organizar archivos (ej: "products/uuid/")
            expires_in: Tiempo de expiración de la URL en segundos (default: 7 días)

        Returns:
            URL presigned para acceder al archivo
        """
        try:
            logger.info(
                f"Subiendo archivo '{file.filename}' con prefijo '{prefix}' al bucket S3 '{self.bucket_name}' (sync)..."
            )
            file_extension = Path(file.filename).suffix
            object_name = (
                f"{prefix}{uuid.uuid4()}{file_extension}"
                if prefix
                else f"{uuid.uuid4()}{file_extension}"
            )
            logger.debug(f"Nombre de objeto único generado: {object_name}")

            file.file.seek(0)
            self.sync_client.upload_fileobj(
                file.file,
                self.bucket_name,
                object_name,
                ExtraArgs={"ContentType": file.content_type},
            )

            logger.info(
                f"Archivo subido exitosamente a S3 como '{object_name}' (sync)."
            )

            # Generar URL pública simple (asumiendo bucket público)
            # Si S3_PUBLIC_DOMAIN está configurado, úsalo; de lo contrario, usa S3_ENDPOINT
            public_domain = settings.S3_PUBLIC_DOMAIN or settings.S3_ENDPOINT
            protocol = "https" if settings.S3_USE_SSL else "http"
            public_url = (
                f"{protocol}://{public_domain}/{self.bucket_name}/{object_name}"
            )

            logger.debug(f"URL pública generada para '{object_name}': {public_url}")

            return public_url

        except ClientError as e:
            logger.error(f"Error al subir el archivo a S3 (sync): {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"No se pudo guardar el archivo en el almacenamiento: {e}",
            )
        finally:
            logger.debug(f"Cerrando el archivo de subida '{file.filename}'.")
            file.close()

    def get_presigned_url_for_object(
        self, object_name: str, expires_in: int = 3600
    ) -> str:
        """
        Genera una URL pre-firmada y temporal para acceder a un objeto (modo síncrono).

        Args:
            object_name: Nombre del objeto en S3
            expires_in: Tiempo de expiración en segundos (por defecto 1 hora)
        """
        try:
            logger.info(
                f"Generando URL pre-firmada para el objeto S3: {object_name} (sync)"
            )
            url = self.sync_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": object_name},
                ExpiresIn=expires_in,
            )
            logger.info("URL pre-firmada generada exitosamente (sync).")
            return url

        except ClientError as e:
            logger.error(
                f"Error al generar URL pre-firmada para '{object_name}' (sync): {e}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se pudo generar la URL para el objeto '{object_name}': {e}",
            )

    def delete_file(self, object_name: str) -> bool:
        """
        Elimina un archivo de S3 (modo síncrono).

        Args:
            object_name: Nombre del objeto a eliminar

        Returns:
            True si se eliminó exitosamente
        """
        try:
            logger.info(f"Eliminando objeto S3: {object_name} (sync)")
            self.sync_client.delete_object(Bucket=self.bucket_name, Key=object_name)
            logger.info(f"Objeto '{object_name}' eliminado exitosamente (sync).")
            return True
        except ClientError as e:
            logger.error(f"Error al eliminar objeto '{object_name}' de S3 (sync): {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"No se pudo eliminar el archivo: {e}",
            )

    def file_exists(self, object_name: str) -> bool:
        """
        Verifica si un archivo existe en S3 (modo síncrono).

        Args:
            object_name: Nombre del objeto a verificar

        Returns:
            True si el archivo existe, False en caso contrario
        """
        try:
            logger.debug(f"Verificando existencia de objeto S3: {object_name} (sync)")
            self.sync_client.head_object(Bucket=self.bucket_name, Key=object_name)
            logger.debug(f"Objeto '{object_name}' existe (sync).")
            return True
        except ClientError as e:
            error_code = int(e.response["Error"]["Code"])
            if error_code == 404:
                logger.debug(f"Objeto '{object_name}' no existe (sync).")
                return False
            logger.error(
                f"Error al verificar existencia de '{object_name}' (sync): {e}"
            )
            raise

    # ==========================================================
    # ⚡ MÉTODOS ASÍNCRONOS
    # ==========================================================

    async def asave_audio_file(self, file: UploadFile) -> str:
        """
        Guarda un archivo de audio en S3 (modo asíncrono).
        """
        protocol = "https" if settings.S3_USE_SSL else "http"
        endpoint_url = f"{protocol}://{settings.S3_ENDPOINT}"

        try:
            logger.info(
                f"Subiendo archivo '{file.filename}' al bucket S3 '{self.bucket_name}' (async)..."
            )
            file_extension = Path(file.filename).suffix
            object_name = f"{uuid.uuid4()}{file_extension}"
            logger.debug(f"Nombre de objeto único generado: {object_name} (async)")

            file.file.seek(0)

            async with self.async_session.client(
                "s3",
                endpoint_url=endpoint_url,
                aws_access_key_id=settings.S3_ACCESS_KEY,
                aws_secret_access_key=settings.S3_SECRET_KEY,
                config=Config(signature_version="s3v4"),
            ) as client:
                await client.upload_fileobj(
                    file.file,
                    self.bucket_name,
                    object_name,
                    ExtraArgs={"ContentType": file.content_type},
                )

            logger.info(
                f"Archivo subido exitosamente a S3 como '{object_name}' (async)."
            )
            return object_name
        except ClientError as e:
            logger.error(f"Error al subir el archivo a S3 (async): {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"No se pudo guardar el archivo en el almacenamiento: {e}",
            )
        finally:
            logger.debug(f"Cerrando el archivo de subida '{file.filename}'.")
            await file.close()

    async def asave_file(
        self, file: UploadFile, prefix: str = "", expires_in: int = 3600 * 24 * 7
    ) -> str:
        """
        Guarda un archivo genérico en S3 con un prefijo opcional y retorna una URL presigned (modo asíncrono).

        Args:
            file: Archivo a subir
            prefix: Prefijo para organizar archivos (ej: "products/uuid/")
            expires_in: Tiempo de expiración de la URL en segundos (default: 7 días)

        Returns:
            URL presigned para acceder al archivo
        """
        protocol = "https" if settings.S3_USE_SSL else "http"
        endpoint_url = f"{protocol}://{settings.S3_ENDPOINT}"

        try:
            logger.info(
                f"Subiendo archivo '{file.filename}' con prefijo '{prefix}' al bucket S3 '{self.bucket_name}' (async)..."
            )
            file_extension = Path(file.filename).suffix
            object_name = (
                f"{prefix}{uuid.uuid4()}{file_extension}"
                if prefix
                else f"{uuid.uuid4()}{file_extension}"
            )
            logger.debug(f"Nombre de objeto único generado: {object_name} (async)")

            file.file.seek(0)

            async with self.async_session.client(
                "s3",
                endpoint_url=endpoint_url,
                aws_access_key_id=settings.S3_ACCESS_KEY,
                aws_secret_access_key=settings.S3_SECRET_KEY,
                config=Config(signature_version="s3v4"),
            ) as client:
                await client.upload_fileobj(
                    file.file,
                    self.bucket_name,
                    object_name,
                    ExtraArgs={"ContentType": file.content_type},
                )

                logger.info(
                    f"Archivo subido exitosamente a S3 como '{object_name}' (async)."
                )

            # Generar URL pública simple (asumiendo bucket público)
            # Si S3_PUBLIC_DOMAIN está configurado, úsalo; de lo contrario, usa S3_ENDPOINT
            public_domain = settings.S3_PUBLIC_DOMAIN or settings.S3_ENDPOINT
            protocol_public = "https" if settings.S3_USE_SSL else "http"
            public_url = (
                f"{protocol_public}://{public_domain}/{self.bucket_name}/{object_name}"
            )

            logger.debug(
                f"URL pública generada para '{object_name}': {public_url} (async)"
            )

            return public_url

        except ClientError as e:
            logger.error(f"Error al subir el archivo a S3 (async): {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"No se pudo guardar el archivo en el almacenamiento: {e}",
            )
        finally:
            logger.debug(f"Cerrando el archivo de subida '{file.filename}'.")
            await file.close()

    async def aget_presigned_url_for_object(
        self, object_name: str, expires_in: int = 3600
    ) -> str:
        """
        Genera una URL pre-firmada y temporal para acceder a un objeto (modo asíncrono).

        Args:
            object_name: Nombre del objeto en S3
            expires_in: Tiempo de expiración en segundos (por defecto 1 hora)
        """
        protocol = "https" if settings.S3_USE_SSL else "http"
        endpoint_url = f"{protocol}://{settings.S3_ENDPOINT}"

        try:
            logger.info(
                f"Generando URL pre-firmada para el objeto S3: {object_name} (async)"
            )

            async with self.async_session.client(
                "s3",
                endpoint_url=endpoint_url,
                aws_access_key_id=settings.S3_ACCESS_KEY,
                aws_secret_access_key=settings.S3_SECRET_KEY,
                config=Config(signature_version="s3v4"),
            ) as client:
                url = await client.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": self.bucket_name, "Key": object_name},
                    ExpiresIn=expires_in,
                )

            logger.info("URL pre-firmada generada exitosamente (async).")
            return url

        except ClientError as e:
            logger.error(
                f"Error al generar URL pre-firmada para '{object_name}' (async): {e}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se pudo generar la URL para el objeto '{object_name}': {e}",
            )

    async def adelete_file(self, object_name: str) -> bool:
        """
        Elimina un archivo de S3 (modo asíncrono).

        Args:
            object_name: Nombre del objeto a eliminar

        Returns:
            True si se eliminó exitosamente
        """
        protocol = "https" if settings.S3_USE_SSL else "http"
        endpoint_url = f"{protocol}://{settings.S3_ENDPOINT}"

        try:
            logger.info(f"Eliminando objeto S3: {object_name} (async)")

            async with self.async_session.client(
                "s3",
                endpoint_url=endpoint_url,
                aws_access_key_id=settings.S3_ACCESS_KEY,
                aws_secret_access_key=settings.S3_SECRET_KEY,
                config=Config(signature_version="s3v4"),
            ) as client:
                await client.delete_object(Bucket=self.bucket_name, Key=object_name)

            logger.info(f"Objeto '{object_name}' eliminado exitosamente (async).")
            return True
        except ClientError as e:
            logger.error(f"Error al eliminar objeto '{object_name}' de S3 (async): {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"No se pudo eliminar el archivo: {e}",
            )

    async def afile_exists(self, object_name: str) -> bool:
        """
        Verifica si un archivo existe en S3 (modo asíncrono).

        Args:
            object_name: Nombre del objeto a verificar

        Returns:
            True si el archivo existe, False en caso contrario
        """
        protocol = "https" if settings.S3_USE_SSL else "http"
        endpoint_url = f"{protocol}://{settings.S3_ENDPOINT}"

        try:
            logger.debug(f"Verificando existencia de objeto S3: {object_name} (async)")

            async with self.async_session.client(
                "s3",
                endpoint_url=endpoint_url,
                aws_access_key_id=settings.S3_ACCESS_KEY,
                aws_secret_access_key=settings.S3_SECRET_KEY,
                config=Config(signature_version="s3v4"),
            ) as client:
                await client.head_object(Bucket=self.bucket_name, Key=object_name)

            logger.debug(f"Objeto '{object_name}' existe (async).")
            return True
        except ClientError as e:
            error_code = int(e.response["Error"]["Code"])
            if error_code == 404:
                logger.debug(f"Objeto '{object_name}' no existe (async).")
                return False
            logger.error(
                f"Error al verificar existencia de '{object_name}' (async): {e}"
            )
            raise
