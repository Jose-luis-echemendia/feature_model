"""
app/core/s3.py

Cliente MinIO para el dominio de Feature Models.

Responsabilidades:
    - Subir recursos asociados a features (documentos/adjuntos/exportaciones)
    - Subir assets públicos (avatares, previews)
    - Generar presigned URLs de descarga con TTL configurable
    - Eliminar objetos huérfanos
    - Garantizar que los buckets existen al arrancar (idempotente)


"""

from __future__ import annotations

import asyncio
import io
from datetime import timedelta
from uuid import UUID

from minio import Minio
from minio.error import S3Error

from app.core.config import settings
from app.core.logging import get_logger

log = get_logger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers internos
# ─────────────────────────────────────────────────────────────────────────────


def _resource_object_name(resource_id: str | UUID, ext: str = "bin") -> str:
    """Nombre de objeto para recurso genérico. Ej: 'resources/<id>.pdf'."""
    normalized_ext = ext.lstrip(".") or "bin"
    return f"resources/{resource_id}.{normalized_ext}"


def _export_object_name(version_id: str | UUID, fmt: str = "json") -> str:
    """Nombre de export de Feature Model. Ej: 'exports/<version>.xml'."""
    normalized_fmt = fmt.lstrip(".") or "json"
    return f"exports/{version_id}.{normalized_fmt}"


def _avatar_object_name(user_id: str | UUID) -> str:
    """Nombre del objeto avatar en MinIO. Ej: 'avatars/abc123.jpg'"""
    return f"avatars/{user_id}.jpg"


def _template_preview_name(template_slug: str) -> str:
    """Nombre del preview de plantilla. Ej: 'templates/modern.png'"""
    return f"templates/{template_slug}.png"


# ─────────────────────────────────────────────────────────────────────────────
# MinIOClient
# ─────────────────────────────────────────────────────────────────────────────


class MinIOClient:
    """
    Wrapper sobre el cliente oficial de MinIO.

    El SDK de MinIO es síncrono — todas las operaciones de I/O se
    ejecutan en un ThreadPoolExecutor mediante asyncio.to_thread()
    para no bloquear el event loop de FastAPI/Celery.
    """

    def __init__(self) -> None:
        raw_secret = settings.MINIO_SECRET_KEY
        secret_key = (
            raw_secret.get_secret_value()
            if hasattr(raw_secret, "get_secret_value")
            else str(raw_secret)
        )

        self._client = Minio(
            endpoint=settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=secret_key,
            secure=settings.MINIO_USE_SSL,
        )

        # Bucket principal y bucket de assets
        self._bucket_primary = getattr(settings, "MINIO_BUCKET_FM", "media")
        self._bucket_assets = getattr(
            settings,
            "MINIO_BUCKET_ASSETS",
            self._bucket_primary,
        )

    # ─────────────────────────────────────────────────────────────────────────
    # Lifecycle — llamar en el startup del lifespan
    # ─────────────────────────────────────────────────────────────────────────

    async def ensure_buckets(self) -> None:
        """
        Crea los buckets necesarios si no existen.
        Operación idempotente — segura para llamar en cada arranque.
        """
        buckets = {
            self._bucket_primary,
            self._bucket_assets,
        }
        for bucket in buckets:
            await asyncio.to_thread(self._ensure_bucket_sync, bucket)

    def _ensure_bucket_sync(self, bucket: str) -> None:
        try:
            if not self._client.bucket_exists(bucket):
                self._client.make_bucket(bucket)
                log.info("minio.bucket.created", bucket=bucket)
            else:
                log.debug("minio.bucket.exists", bucket=bucket)
        except S3Error as exc:
            log.error("minio.bucket.error", bucket=bucket, error=str(exc))
            raise

    # ─────────────────────────────────────────────────────────────────────────
    # Recursos y exportaciones de Feature Model
    # ─────────────────────────────────────────────────────────────────────────

    async def upload_resource_file(
        self,
        resource_id: str | UUID,
        content_bytes: bytes,
        *,
        ext: str = "bin",
        content_type: str = "application/octet-stream",
    ) -> str:
        """
        Sube un recurso asociado al dominio Feature Model.

        Returns:
            Nombre del objeto en MinIO (no la URL — usa `get_resource_download_url`).
        """
        object_name = _resource_object_name(resource_id, ext)
        data = io.BytesIO(content_bytes)
        size = len(content_bytes)

        await asyncio.to_thread(
            self._client.put_object,
            self._bucket_primary,
            object_name,
            data,
            size,
            content_type=content_type,
            metadata={
                "resource-id": str(resource_id),
                "generator": settings.APP_NAME,
            },
        )

        log.info(
            "minio.resource.uploaded",
            resource_id=str(resource_id),
            object_name=object_name,
            size_bytes=size,
        )
        return object_name

    async def get_resource_download_url(
        self,
        resource_id: str | UUID,
        *,
        ext: str = "bin",
        filename: str | None = None,
    ) -> str:
        """
        Genera un presigned URL de descarga para un recurso.
        El URL es válido durante settings.MINIO_PRESIGN_TTL segundos.
        """
        object_name = _resource_object_name(resource_id, ext)
        download_name = filename or f"resource-{resource_id}.{ext.lstrip('.') or 'bin'}"
        url = await asyncio.to_thread(
            self._client.presigned_get_object,
            self._bucket_primary,
            object_name,
            expires=timedelta(seconds=settings.MINIO_PRESIGN_TTL),
            response_headers={
                "response-content-disposition": (
                    f'attachment; filename="{download_name}"'
                ),
            },
        )
        log.debug(
            "minio.resource.presigned",
            resource_id=str(resource_id),
            ttl=settings.MINIO_PRESIGN_TTL,
        )
        return url

    async def delete_resource_file(
        self,
        resource_id: str | UUID,
        *,
        ext: str = "bin",
    ) -> None:
        """Elimina un recurso del almacenamiento de objetos."""
        object_name = _resource_object_name(resource_id, ext)
        try:
            await asyncio.to_thread(
                self._client.remove_object,
                self._bucket_primary,
                object_name,
            )
            log.info("minio.resource.deleted", resource_id=str(resource_id))
        except S3Error as exc:
            # Si ya no existe, no es un error crítico
            if exc.code == "NoSuchKey":
                log.warning("minio.resource.not_found", resource_id=str(resource_id))
            else:
                log.error(
                    "minio.resource.delete_error",
                    resource_id=str(resource_id),
                    error=str(exc),
                )
                raise

    async def resource_file_exists(
        self,
        resource_id: str | UUID,
        *,
        ext: str = "bin",
    ) -> bool:
        """Comprueba si el recurso existe en MinIO."""
        object_name = _resource_object_name(resource_id, ext)
        try:
            await asyncio.to_thread(
                self._client.stat_object,
                self._bucket_primary,
                object_name,
            )
            return True
        except S3Error:
            return False

    async def upload_feature_model_export(
        self,
        version_id: str | UUID,
        export_bytes: bytes,
        *,
        fmt: str = "json",
        content_type: str = "application/json",
    ) -> str:
        """Sube una exportación serializada de una versión del Feature Model."""
        object_name = _export_object_name(version_id, fmt)
        data = io.BytesIO(export_bytes)

        await asyncio.to_thread(
            self._client.put_object,
            self._bucket_primary,
            object_name,
            data,
            len(export_bytes),
            content_type=content_type,
            metadata={
                "version-id": str(version_id),
                "export-format": fmt,
            },
        )

        log.info(
            "minio.export.uploaded", version_id=str(version_id), object_name=object_name
        )
        return object_name

    async def get_feature_model_export_url(
        self,
        version_id: str | UUID,
        *,
        fmt: str = "json",
    ) -> str:
        """Obtiene URL de descarga firmada para una exportación de versión."""
        object_name = _export_object_name(version_id, fmt)
        normalized_fmt = fmt.lstrip(".") or "json"
        return await asyncio.to_thread(
            self._client.presigned_get_object,
            self._bucket_primary,
            object_name,
            expires=timedelta(seconds=settings.MINIO_PRESIGN_TTL),
            response_headers={
                "response-content-disposition": (
                    f'attachment; filename="feature-model-{version_id}.{normalized_fmt}"'
                ),
            },
        )

    # ─────────────────────────────────────────────────────────────────────────
    # Avatares — bucket de assets
    # ─────────────────────────────────────────────────────────────────────────

    async def upload_avatar(
        self,
        user_id: str | UUID,
        image_bytes: bytes,
        content_type: str = "image/jpeg",
    ) -> str:
        """
        Sube el avatar del usuario. Sobreescribe si ya existe.

        Returns:
            URL pública del avatar (los assets son públicos por política del bucket).
        """
        object_name = _avatar_object_name(user_id)
        data = io.BytesIO(image_bytes)

        await asyncio.to_thread(
            self._client.put_object,
            self._bucket_assets,
            object_name,
            data,
            len(image_bytes),
            content_type=content_type,
        )

        url = self._public_url(self._bucket_assets, object_name)
        log.info("minio.avatar.uploaded", user_id=str(user_id))
        return url

    async def delete_avatar(self, user_id: str | UUID) -> None:
        """Elimina el avatar del usuario."""
        object_name = _avatar_object_name(user_id)
        try:
            await asyncio.to_thread(
                self._client.remove_object,
                self._bucket_assets,
                object_name,
            )
            log.info("minio.avatar.deleted", user_id=str(user_id))
        except S3Error as exc:
            if exc.code != "NoSuchKey":
                raise

    # ─────────────────────────────────────────────────────────────────────────
    # Previews de plantillas — bucket de assets
    # ─────────────────────────────────────────────────────────────────────────

    async def upload_template_preview(
        self,
        template_slug: str,
        image_bytes: bytes,
        content_type: str = "image/png",
    ) -> str:
        """
        Sube la imagen de preview de una plantilla.
        Solo llamado desde endpoints de administración.

        Returns:
            URL pública del preview.
        """
        object_name = _template_preview_name(template_slug)
        data = io.BytesIO(image_bytes)

        await asyncio.to_thread(
            self._client.put_object,
            self._bucket_assets,
            object_name,
            data,
            len(image_bytes),
            content_type=content_type,
        )

        url = self._public_url(self._bucket_assets, object_name)
        log.info("minio.template_preview.uploaded", slug=template_slug)
        return url

    # ─────────────────────────────────────────────────────────────────────────
    # Helpers
    # ─────────────────────────────────────────────────────────────────────────

    def _public_url(self, bucket: str, object_name: str) -> str:
        """
        Construye la URL pública de un objeto en un bucket sin acceso restringido.
        Para assets (avatares, previews) que son de lectura pública.
        """
        scheme = "https" if settings.MINIO_USE_SSL else "http"
        return f"{scheme}://{settings.MINIO_ENDPOINT}/{bucket}/{object_name}"

    async def health_check(self) -> bool:
        """Verifica que MinIO esté disponible listando los buckets."""
        try:
            await asyncio.to_thread(list, self._client.list_buckets())
            return True
        except Exception as exc:
            log.error("minio.health_check.failed", error=str(exc))
            return False


# ── Singleton ─────────────────────────────────────────────────────────────────
minio_client = MinIOClient()
