"""
app/core/minio.py

Cliente MinIO para el dominio CV.

Responsabilidades:
  - Subir PDFs generados al bucket 'cvs'
  - Subir avatares e imágenes de plantilla al bucket 'cv-assets'
  - Generar presigned URLs de descarga con TTL configurable
  - Eliminar objetos (limpieza de PDFs expirados)
  - Garantizar que los buckets existen al arrancar (idempotente)

Uso en servicios:
    from app.core.minio import minio_client

    url = await minio_client.upload_pdf(cv_id, pdf_bytes)
    presigned = await minio_client.get_download_url(cv_id)
    await minio_client.delete_pdf(cv_id)
"""

from __future__ import annotations

import asyncio
import io
from datetime import timedelta
from functools import lru_cache
from uuid import UUID

from minio import Minio
from minio.error import S3Error

from app.core.config import settings
from app.core.logging import get_logger

log = get_logger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers internos
# ─────────────────────────────────────────────────────────────────────────────


def _cv_object_name(cv_id: str | UUID) -> str:
    """Nombre del objeto PDF en MinIO. Ej: 'pdfs/abc123.pdf'"""
    return f"pdfs/{cv_id}.pdf"


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
        self._client = Minio(
            endpoint=settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY.get_secret_value(),
            secure=settings.MINIO_USE_SSL,
        )
        self._bucket_cvs = settings.MINIO_BUCKET_CVS
        self._bucket_assets = settings.MINIO_BUCKET_ASSETS

    # ─────────────────────────────────────────────────────────────────────────
    # Lifecycle — llamar en el startup del lifespan
    # ─────────────────────────────────────────────────────────────────────────

    async def ensure_buckets(self) -> None:
        """
        Crea los buckets necesarios si no existen.
        Operación idempotente — segura para llamar en cada arranque.
        """
        for bucket in (self._bucket_cvs, self._bucket_assets):
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
    # PDFs — bucket 'cvs'
    # ─────────────────────────────────────────────────────────────────────────

    async def upload_pdf(
        self,
        cv_id: str | UUID,
        pdf_bytes: bytes,
    ) -> str:
        """
        Sube el PDF generado al bucket 'cvs'.

        Returns:
            Nombre del objeto en MinIO (no la URL — usa get_download_url para eso).
        """
        object_name = _cv_object_name(cv_id)
        data = io.BytesIO(pdf_bytes)
        size = len(pdf_bytes)

        await asyncio.to_thread(
            self._client.put_object,
            self._bucket_cvs,
            object_name,
            data,
            size,
            content_type="application/pdf",
            metadata={
                "cv-id": str(cv_id),
                "generator": settings.APP_NAME,
            },
        )

        log.info("minio.pdf.uploaded", cv_id=str(cv_id), size_bytes=size)
        return object_name

    async def get_download_url(self, cv_id: str | UUID) -> str:
        """
        Genera un presigned URL de descarga para el PDF de un CV.
        El URL es válido durante settings.MINIO_PRESIGN_TTL segundos.
        """
        object_name = _cv_object_name(cv_id)
        url = await asyncio.to_thread(
            self._client.presigned_get_object,
            self._bucket_cvs,
            object_name,
            expires=timedelta(seconds=settings.MINIO_PRESIGN_TTL),
            response_headers={
                "response-content-disposition": (
                    f'attachment; filename="cv-{cv_id}.pdf"'
                ),
            },
        )
        log.debug(
            "minio.pdf.presigned", cv_id=str(cv_id), ttl=settings.MINIO_PRESIGN_TTL
        )
        return url

    async def delete_pdf(self, cv_id: str | UUID) -> None:
        """Elimina el PDF de MinIO. Llamado por la tarea de limpieza."""
        object_name = _cv_object_name(cv_id)
        try:
            await asyncio.to_thread(
                self._client.remove_object,
                self._bucket_cvs,
                object_name,
            )
            log.info("minio.pdf.deleted", cv_id=str(cv_id))
        except S3Error as exc:
            # Si ya no existe, no es un error crítico
            if exc.code == "NoSuchKey":
                log.warning("minio.pdf.not_found", cv_id=str(cv_id))
            else:
                log.error("minio.pdf.delete_error", cv_id=str(cv_id), error=str(exc))
                raise

    async def pdf_exists(self, cv_id: str | UUID) -> bool:
        """Comprueba si el PDF de un CV existe en MinIO."""
        object_name = _cv_object_name(cv_id)
        try:
            await asyncio.to_thread(
                self._client.stat_object,
                self._bucket_cvs,
                object_name,
            )
            return True
        except S3Error:
            return False

    # ─────────────────────────────────────────────────────────────────────────
    # Avatares — bucket 'cv-assets'
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
    # Previews de plantillas — bucket 'cv-assets'
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
