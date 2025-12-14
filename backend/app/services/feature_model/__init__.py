"""
Módulo de servicios para los Feature Model.

Este módulo implementa seis componentes fundamentales para la validación
y análisis de modelos de características:

1. Validador Lógico (SAT/SMT Solver): Verifica consistencia y satisfacibilidad
2. Generador de Configuraciones: Construye configuraciones válidas
3. Analizador Estructural: Detecta dead features, redundancias, etc.
4. Constructor de Árboles: Representa jerarquías y relaciones entre características
5. Exportador de Modelos: Convierte modelos a formatos estándar (XML, TVL, DIMACS, etc)
6. Manejador de versionado de los modelos
"""

from .fm_logical_validator import FeatureModelLogicalValidator
from .fm_configuration_generator import FeatureModelConfigurationGenerator
from .fm_structural_analyzer import FeatureModelStructuralAnalyzer
from .fm_tree_builder import FeatureModelTreeBuilder
from .fm_export import FeatureModelExportService
from .fm_version_manager import FeatureModelVersionManager

__all__ = [
    "FeatureModelLogicalValidator",
    "FeatureModelConfigurationGenerator",
    "FeatureModelStructuralAnalyzer",
    "FeatureModelTreeBuilder",
    "FeatureModelExportService",
    "FeatureModelVersionManager",
]
