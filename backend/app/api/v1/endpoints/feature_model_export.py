"""
Endpoint para exportar Feature Models a diferentes formatos estándar.
"""

import uuid

from fastapi import APIRouter, Depends, Path
from fastapi.responses import Response

from sqlmodel import select

from app.api.deps import (
    AsyncCurrentUser,
    get_verified_user,
    AsyncFeatureModelVersionRepoDep,
)
from app.models import FeatureModelVersion
from app.services.feature_model import FeatureModelExportService
from app.enums import ExportFormat, ModelStatus
from app.exceptions import (
    NoPublishedVersionException,
    FeatureModelVersionNotFoundException,
    UnsupportedExportFormatException,
    ExportFailedException,
)


router = APIRouter(
    prefix="/feature-models",
    tags=["Feature Models - Export"],
    dependencies=[Depends(get_verified_user)],
)


# ============================================================================
# IMPORTANTE: Las rutas más específicas (/latest/) deben ir ANTES que las
# rutas con parámetros variables (/{version_id}/) para evitar conflictos
# ============================================================================


@router.get(
    "/{model_id}/versions/latest/export/{format}",
    summary="Export latest published version to specified format",
    description="""
    Export the latest PUBLISHED version of a feature model to the specified format.
    
    This endpoint automatically finds the most recent published version and exports it.
    
    **Supported formats:**
    
    1. **xml** (FeatureIDE XML)
       - Compatible with FeatureIDE Eclipse plugin
       - Most widely used format in SPL community
       - Supports all feature model elements
       - Use for: FeatureIDE integration, academic research
    
    2. **splot_xml** (SPLOT XML)
       - Compatible with S.P.L.O.T online tool
       - Used in many academic papers
       - Use for: SPLOT tool, benchmark datasets
    
    3. **tvl** (Textual Variability Language)
       - Human-readable textual format
       - Easy to edit and version control
       - Use for: Code reviews, Git diffs
    
    4. **dimacs** (DIMACS CNF)
       - Format for SAT solvers
       - Converts feature model to Boolean constraints
       - Includes variable mapping in comments
       - Use for: Automated analysis, constraint solving
    
    5. **json** (Simple JSON)
       - Easy to parse and manipulate
       - Good for web applications
       - Use for: Web visualizers, custom tools
    
    6. **uvl** (Universal Variability Language)
       - Modern standardized format
       - Growing adoption in community
       - Use for: Tool interoperability, future-proofing
    
    7. **dot** (Graphviz)
       - Generates graph visualization
       - Can be rendered with Graphviz tools
       - Use for: Documentation, presentations
    
    8. **mermaid** (Mermaid Diagrams)
       - Renders in Markdown, GitHub, GitLab
       - Interactive diagrams
       - Use for: Documentation, README files
    
    **Response content types:**
    - XML formats: `application/xml`
    - JSON format: `application/json`
    - Text formats (TVL, DIMACS, DOT, Mermaid): `text/plain`
    
    **Performance:**
    - Typical export time: 50-200ms for models with <1000 features
    - Large models (>2000 features) may take 500ms-1s
    
    **Use cases:**
    - Integration with external SPL tools (FeatureIDE, SPLOT)
    - Analysis with SAT solvers (DIMACS)
    - Documentation generation (Mermaid, DOT)
    - Data exchange (JSON, UVL)
    
    **Note:** Only exports PUBLISHED versions. If no published version exists, returns 404.
    """,
    responses={
        200: {
            "description": "Feature model exported successfully",
            "content": {
                "application/xml": {
                    "example": "<?xml version='1.0'?><featureModel>...</featureModel>"
                },
                "application/json": {"example": {"name": "MyModel", "version": 1}},
                "text/plain": {
                    "example": "graph TD\n  root[Root]\n  root --> child1[Child1]"
                },
            },
        },
        404: {"description": "No published version found for this feature model"},
        400: {"description": "Invalid export format"},
    },
)
async def export_latest_feature_model(
    *,
    model_id: uuid.UUID = Path(..., description="Feature Model UUID"),
    format: ExportFormat = Path(..., description="Export format"),
    version_repo: AsyncFeatureModelVersionRepoDep,
    current_user: AsyncCurrentUser,
) -> Response:
    """Export the latest published version to the specified format."""
    # Buscar la última versión publicada
    stmt = (
        select(FeatureModelVersion)
        .where(
            FeatureModelVersion.feature_model_id == model_id,
            FeatureModelVersion.status == ModelStatus.PUBLISHED,
        )
        .order_by(FeatureModelVersion.version_number.desc())
        .limit(1)
    )

    result = await version_repo.session.execute(stmt)
    latest_version = result.scalar_one_or_none()

    if not latest_version:
        raise NoPublishedVersionException(model_id=str(model_id))

    # Redirigir a la función principal
    return await export_feature_model(
        model_id=model_id,
        version_id=latest_version.id,
        format=format,
        version_repo=version_repo,
        current_user=current_user,
    )


@router.get(
    "/{model_id}/versions/{version_id}/export/{format}",
    summary="Export feature model to specified format",
    description="""
    Export a specific version of a feature model to the specified format.
    
    This endpoint allows you to export any version (DRAFT, IN_REVIEW, PUBLISHED, or ARCHIVED)
    to various standard formats used in Software Product Line engineering.
    
    **Supported formats:**
    
    1. **xml** (FeatureIDE XML)
       - Compatible with FeatureIDE Eclipse plugin
       - Most widely used format in SPL community
       - Supports all feature model elements
       - Use for: FeatureIDE integration, academic research
    
    2. **splot_xml** (SPLOT XML)
       - Compatible with S.P.L.O.T online tool
       - Used in many academic papers
       - Use for: SPLOT tool, benchmark datasets
    
    3. **tvl** (Textual Variability Language)
       - Human-readable textual format
       - Easy to edit and version control
       - Use for: Code reviews, Git diffs
    
    4. **dimacs** (DIMACS CNF)
       - Format for SAT solvers
       - Converts feature model to Boolean constraints
       - Includes variable mapping in comments
       - Use for: Automated analysis, constraint solving
    
    5. **json** (Simple JSON)
       - Easy to parse and manipulate
       - Good for web applications
       - Use for: Web visualizers, custom tools
    
    6. **uvl** (Universal Variability Language)
       - Modern standardized format
       - Growing adoption in community
       - Use for: Tool interoperability, future-proofing
    
    7. **dot** (Graphviz)
       - Generates graph visualization
       - Can be rendered with Graphviz tools
       - Use for: Documentation, presentations
    
    8. **mermaid** (Mermaid Diagrams)
       - Renders in Markdown, GitHub, GitLab
       - Interactive diagrams
       - Use for: Documentation, README files
    
    **Response content types:**
    - XML formats: `application/xml`
    - JSON format: `application/json`
    - Text formats (TVL, DIMACS, DOT, Mermaid): `text/plain`
    
    **Performance:**
    - Typical export time: 50-200ms for models with <1000 features
    - Large models (>2000 features) may take 500ms-1s
    
    **Examples:**
    ```bash
    # Export to FeatureIDE XML
    curl -o model.xml "http://api/feature-models/{id}/versions/{vid}/export/xml"
    
    # Export to DIMACS for SAT solver
    curl -o model.cnf "http://api/feature-models/{id}/versions/{vid}/export/dimacs"
    
    # Export to Mermaid for documentation
    curl "http://api/feature-models/{id}/versions/{vid}/export/mermaid" >> README.md
    ```
    """,
    responses={
        200: {
            "description": "Feature model exported successfully",
            "content": {
                "application/xml": {},
                "application/json": {},
                "text/plain": {},
            },
        },
        404: {"description": "Feature model version not found"},
        400: {"description": "Invalid export format"},
    },
)
async def export_feature_model(
    *,
    model_id: uuid.UUID = Path(..., description="Feature Model UUID"),
    version_id: uuid.UUID = Path(..., description="Version UUID"),
    format: ExportFormat = Path(..., description="Export format"),
    version_repo: AsyncFeatureModelVersionRepoDep,
    current_user: AsyncCurrentUser,
) -> Response:
    """Export a specific version to the specified format."""
    # Obtener la versión con todas las relaciones cargadas
    version = await version_repo.get_version_with_full_structure(version_id)

    if not version or version.feature_model_id != model_id:
        raise FeatureModelVersionNotFoundException(version_id=str(version_id))

    # Verificar que el usuario tenga acceso a esta versión
    # TODO: Implementar lógica de permisos según el status de la versión

    # Crear el servicio de exportación
    try:
        export_service = FeatureModelExportService(version)
        content = export_service.export(format)
    except ValueError as e:
        raise UnsupportedExportFormatException(format=format.value)
    except Exception as e:
        raise ExportFailedException(format=format.value, reason=str(e))

    # Determinar content type y nombre de archivo
    content_types = {
        ExportFormat.XML: "application/xml",
        ExportFormat.SPLOT_XML: "application/xml",
        ExportFormat.JSON: "application/json",
        ExportFormat.TVL: "text/plain",
        ExportFormat.DIMACS: "text/plain",
        ExportFormat.UVL: "text/plain",
        ExportFormat.DOT: "text/plain",
        ExportFormat.MERMAID: "text/plain",
    }

    file_extensions = {
        ExportFormat.XML: "xml",
        ExportFormat.SPLOT_XML: "xml",
        ExportFormat.JSON: "json",
        ExportFormat.TVL: "tvl",
        ExportFormat.DIMACS: "cnf",
        ExportFormat.UVL: "uvl",
        ExportFormat.DOT: "dot",
        ExportFormat.MERMAID: "mmd",
    }

    content_type = content_types.get(format, "text/plain")
    extension = file_extensions.get(format, "txt")

    # Generar nombre de archivo seguro
    model_name = version.feature_model.name.replace(" ", "_").replace("/", "_")
    filename = f"{model_name}_v{version.version_number}.{extension}"

    return Response(
        content=content,
        media_type=content_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )
