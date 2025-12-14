"""
Ejemplos de uso del Motor de Validación de Feature Models.

Este archivo demuestra cómo utilizar los tres componentes principales:
1. LogicalValidator - Validación formal de consistencia
2. ConfigurationGenerator - Generación de configuraciones válidas
3. StructuralAnalyzer - Análisis topológico del modelo
"""

from typing import Dict, List

from app.enums import AnalysisType, GenerationStrategy
from app.services.feature_model import (
    FeatureModelLogicalValidator,
    FeatureModelConfigurationGenerator,
    FeatureModelStructuralAnalyzer,
)


def create_sample_feature_model() -> tuple[List[Dict], List[Dict], List[Dict]]:
    """
    Crea un Feature Model de ejemplo: Sistema de E-Learning.

    Estructura:
        ELearningPlatform (root)
        ├── UserManagement (mandatory)
        │   ├── Authentication (mandatory)
        │   └── Profile (optional)
        ├── Content (mandatory)
        │   ├── Videos (optional)
        │   ├── Documents (optional)
        │   └── Quizzes (mandatory)
        └── Analytics (optional)
            └── Reports (optional)

    Constraints:
    - Analytics REQUIRES Reports
    - Videos EXCLUDES Documents (ejemplo de restricción)
    """
    features = [
        {
            "id": "root",
            "name": "ELearningPlatform",
            "parent_id": None,
        },
        {
            "id": "user_mgmt",
            "name": "UserManagement",
            "parent_id": "root",
        },
        {
            "id": "auth",
            "name": "Authentication",
            "parent_id": "user_mgmt",
        },
        {
            "id": "profile",
            "name": "Profile",
            "parent_id": "user_mgmt",
        },
        {
            "id": "content",
            "name": "Content",
            "parent_id": "root",
        },
        {
            "id": "videos",
            "name": "Videos",
            "parent_id": "content",
        },
        {
            "id": "documents",
            "name": "Documents",
            "parent_id": "content",
        },
        {
            "id": "quizzes",
            "name": "Quizzes",
            "parent_id": "content",
        },
        {
            "id": "analytics",
            "name": "Analytics",
            "parent_id": "root",
        },
        {
            "id": "reports",
            "name": "Reports",
            "parent_id": "analytics",
        },
    ]

    relations = [
        # Root -> UserManagement (mandatory)
        {
            "parent_id": "root",
            "child_id": "user_mgmt",
            "relation_type": "mandatory",
        },
        # UserManagement -> Authentication (mandatory)
        {
            "parent_id": "user_mgmt",
            "child_id": "auth",
            "relation_type": "mandatory",
        },
        # UserManagement -> Profile (optional)
        {
            "parent_id": "user_mgmt",
            "child_id": "profile",
            "relation_type": "optional",
        },
        # Root -> Content (mandatory)
        {
            "parent_id": "root",
            "child_id": "content",
            "relation_type": "mandatory",
        },
        # Content -> Videos (optional)
        {
            "parent_id": "content",
            "child_id": "videos",
            "relation_type": "optional",
        },
        # Content -> Documents (optional)
        {
            "parent_id": "content",
            "child_id": "documents",
            "relation_type": "optional",
        },
        # Content -> Quizzes (mandatory)
        {
            "parent_id": "content",
            "child_id": "quizzes",
            "relation_type": "mandatory",
        },
        # Root -> Analytics (optional)
        {
            "parent_id": "root",
            "child_id": "analytics",
            "relation_type": "optional",
        },
        # Analytics -> Reports (optional)
        {
            "parent_id": "analytics",
            "child_id": "reports",
            "relation_type": "optional",
        },
    ]

    constraints = [
        {
            "expr_text": "Analytics REQUIRES Reports",
            "description": "Si Analytics está activo, Reports debe estarlo",
        },
        {
            "expr_text": "Videos EXCLUDES Documents",
            "description": "No se pueden tener Videos y Documents simultáneamente",
        },
    ]

    return features, relations, constraints


def example_1_validate_model():
    """Ejemplo 1: Validar consistencia de un Feature Model."""
    print("\n" + "=" * 60)
    print("EJEMPLO 1: VALIDACIÓN DE CONSISTENCIA DEL MODELO")
    print("=" * 60)

    features, relations, constraints = create_sample_feature_model()

    validator = FeatureModelLogicalValidator()
    result = validator.validate_feature_model(features, relations, constraints)

    print(f"\n🔍 Validando Feature Model: 'ELearningPlatform'")
    print(f"   Total features: {len(features)}")
    print(f"   Total relations: {len(relations)}")
    print(f"   Total constraints: {len(constraints)}")

    if result.is_valid:
        print(f"\n✅ El modelo es CONSISTENTE y SATISFACIBLE")
        if result.satisfying_assignment:
            print(f"\n📋 Ejemplo de configuración válida:")
            for feature_id, selected in result.satisfying_assignment.items():
                if selected:
                    feature = next(
                        (f for f in features if str(f["id"]) == feature_id), None
                    )
                    if feature:
                        print(f"   ✓ {feature['name']}")
    else:
        print(f"\n❌ El modelo tiene ERRORES:")
        for error in result.errors:
            print(f"   • {error}")

    if result.warnings:
        print(f"\n⚠️  Advertencias:")
        for warning in result.warnings:
            print(f"   • {warning}")


def example_2_validate_user_configuration():
    """Ejemplo 2: Validar una configuración específica del usuario."""
    print("\n" + "=" * 60)
    print("EJEMPLO 2: VALIDACIÓN DE CONFIGURACIÓN DE USUARIO")
    print("=" * 60)

    features, relations, constraints = create_sample_feature_model()
    validator = FeatureModelLogicalValidator()

    # Configuración válida
    print("\n📝 Caso 1: Configuración VÁLIDA")
    valid_selection = [
        "root",
        "user_mgmt",
        "auth",
        "profile",
        "content",
        "videos",
        "quizzes",
    ]
    print(f"   Selección: {valid_selection}")

    result = validator.validate_configuration(
        features, relations, constraints, valid_selection
    )

    if result.is_valid:
        print("   ✅ Configuración VÁLIDA")
    else:
        print("   ❌ Configuración INVÁLIDA")
        for error in result.errors:
            print(f"      • {error}")

    # Configuración inválida (viola constraint)
    print("\n📝 Caso 2: Configuración INVÁLIDA (viola constraint)")
    invalid_selection = [
        "root",
        "user_mgmt",
        "auth",
        "content",
        "videos",
        "documents",  # ❌ Viola: Videos EXCLUDES Documents
        "quizzes",
        "analytics",  # ❌ Viola: Analytics REQUIRES Reports (pero Reports no está)
    ]
    print(f"   Selección: {invalid_selection}")

    result = validator.validate_configuration(
        features, relations, constraints, invalid_selection
    )

    if result.is_valid:
        print("   ✅ Configuración VÁLIDA")
    else:
        print("   ❌ Configuración INVÁLIDA (esperado)")
        for error in result.errors:
            print(f"      • {error}")


def example_3_generate_configurations():
    """Ejemplo 3: Generar configuraciones válidas automáticamente."""
    print("\n" + "=" * 60)
    print("EJEMPLO 3: GENERACIÓN DE CONFIGURACIONES VÁLIDAS")
    print("=" * 60)

    features, relations, constraints = create_sample_feature_model()
    generator = FeatureModelConfigurationGenerator()

    # Generar con estrategia GREEDY
    print("\n🎲 Estrategia: GREEDY (determinista)")
    result_greedy = generator.generate_valid_configuration(
        features, relations, constraints, strategy=GenerationStrategy.GREEDY
    )

    if result_greedy.success:
        print(f"   ✅ Configuración generada:")
        print(f"      Features seleccionadas: {len(result_greedy.selected_features)}")
        print(f"      Score: {result_greedy.score:.2f}")
        print(f"      Iteraciones: {result_greedy.iterations}")
        print(f"\n   📋 Features incluidas:")
        for fid in result_greedy.selected_features:
            feature = next((f for f in features if str(f["id"]) == fid), None)
            if feature:
                print(f"      ✓ {feature['name']}")

    # Generar con estrategia RANDOM
    print("\n🎲 Estrategia: RANDOM (no determinista)")
    result_random = generator.generate_valid_configuration(
        features, relations, constraints, strategy=GenerationStrategy.RANDOM
    )

    if result_random.success:
        print(f"   ✅ Configuración generada:")
        print(f"      Features seleccionadas: {len(result_random.selected_features)}")
        print(f"      Score: {result_random.score:.2f}")

    # Generar múltiples configuraciones
    print("\n🎲 Generando 5 configuraciones diversas:")
    multiple_results = generator.generate_multiple_configurations(
        features, relations, constraints, count=5, diverse=True
    )

    for i, result in enumerate(multiple_results):
        print(
            f"   Config {i+1}: {len(result.selected_features)} features "
            f"(score: {result.score:.2f})"
        )


def example_4_complete_partial_configuration():
    """Ejemplo 4: Completar una configuración parcial del usuario."""
    print("\n" + "=" * 60)
    print("EJEMPLO 4: COMPLETAR CONFIGURACIÓN PARCIAL")
    print("=" * 60)

    features, relations, constraints = create_sample_feature_model()
    generator = FeatureModelConfigurationGenerator()

    # Usuario seleccionó solo algunas features
    partial_selection = {
        "root": True,
        "user_mgmt": True,
        "auth": True,
        "analytics": True,  # Usuario quiere Analytics
    }

    print("\n📝 Selección parcial del usuario:")
    for fid, selected in partial_selection.items():
        feature = next((f for f in features if str(f["id"]) == fid), None)
        if feature and selected:
            print(f"   ✓ {feature['name']}")

    print("\n🔧 Completando configuración automáticamente...")
    result = generator.complete_partial_configuration(
        features, relations, constraints, partial_selection
    )

    if result.success:
        print(f"\n✅ Configuración completada:")
        print(f"   Total features: {len(result.selected_features)}")
        print(f"\n   📋 Configuración final:")
        for fid in result.selected_features:
            feature = next((f for f in features if str(f["id"]) == fid), None)
            if feature:
                prefix = "★" if fid in partial_selection else " "
                print(f"   {prefix} ✓ {feature['name']}")
        print("\n   (★ = seleccionado por usuario)")


def example_5_structural_analysis():
    """Ejemplo 5: Análisis estructural del modelo."""
    print("\n" + "=" * 60)
    print("EJEMPLO 5: ANÁLISIS ESTRUCTURAL")
    print("=" * 60)

    features, relations, constraints = create_sample_feature_model()
    analyzer = FeatureModelStructuralAnalyzer()

    # Análisis de dead features
    print("\n🔍 Analizando Dead Features...")
    dead_features_result = analyzer.analyze_feature_model(
        features, relations, constraints, analysis_types=[AnalysisType.DEAD_FEATURES]
    )[AnalysisType.DEAD_FEATURES]

    if dead_features_result.issues:
        print(f"   ⚠️  Se encontraron {len(dead_features_result.issues)} problemas:")
        for issue in dead_features_result.issues:
            print(f"      • {issue.description}")
    else:
        print(f"   ✅ No hay dead features")
        print(
            f"      Features alcanzables: {dead_features_result.metrics['reachable_features']}"
        )

    # Análisis de complejidad
    print("\n📊 Métricas de Complejidad:")
    complexity_result = analyzer.analyze_feature_model(
        features,
        relations,
        constraints,
        analysis_types=[AnalysisType.COMPLEXITY_METRICS],
    )[AnalysisType.COMPLEXITY_METRICS]

    metrics = complexity_result.metrics
    print(f"   • Profundidad máxima: {metrics['max_depth']}")
    print(f"   • Total features: {metrics['total_features']}")
    print(f"   • Features hoja: {metrics['leaf_features']}")
    print(f"   • Factor ramificación: {metrics['avg_branching_factor']}")
    print(f"   • Densidad constraints: {metrics['constraint_density']}")
    print(f"   • Total constraints: {metrics['total_constraints']}")

    if complexity_result.issues:
        print(f"\n   ⚠️  Advertencias de complejidad:")
        for issue in complexity_result.issues:
            print(f"      • {issue.description}")

    # Análisis de impacto de una feature
    print("\n🎯 Análisis de Impacto - Feature 'Content':")
    impact = analyzer.calculate_feature_impact(
        features, relations, constraints, "content"
    )
    print(f"   • Dependientes directos: {impact['direct_dependents']}")
    print(f"   • Dependientes transitivos: {impact['transitive_dependents']}")
    print(f"   • Profundidad: {impact['depth']}")
    print(f"   • Constraints involucradas: {impact['constraints_count']}")
    print(f"   • Score de impacto: {impact['impact_score']}")


def example_6_full_workflow():
    """Ejemplo 6: Flujo completo de validación y análisis."""
    print("\n" + "=" * 60)
    print("EJEMPLO 6: FLUJO COMPLETO DE TRABAJO")
    print("=" * 60)

    features, relations, constraints = create_sample_feature_model()

    # Paso 1: Análisis estructural previo
    print("\n📊 PASO 1: Análisis estructural previo")
    analyzer = FeatureModelStructuralAnalyzer()
    structural_results = analyzer.analyze_feature_model(
        features, relations, constraints
    )

    dead_count = len(structural_results[AnalysisType.DEAD_FEATURES].issues)
    complexity = structural_results[AnalysisType.COMPLEXITY_METRICS].metrics

    print(f"   • Dead features: {dead_count}")
    print(
        f"   • Complejidad: depth={complexity['max_depth']}, "
        f"features={complexity['total_features']}"
    )

    # Paso 2: Validación lógica
    print("\n🔍 PASO 2: Validación lógica del modelo")
    validator = FeatureModelLogicalValidator()
    validation = validator.validate_feature_model(features, relations, constraints)

    if validation.is_valid:
        print(f"   ✅ Modelo consistente")
    else:
        print(f"   ❌ Modelo inconsistente")
        return

    # Paso 3: Generación de configuraciones
    print("\n🎲 PASO 3: Generación de configuraciones")
    generator = FeatureModelConfigurationGenerator()
    configs = generator.generate_multiple_configurations(
        features, relations, constraints, count=3, diverse=True
    )
    print(f"   ✅ Generadas {len(configs)} configuraciones válidas")

    # Paso 4: Validar configuración de usuario
    print("\n📝 PASO 4: Validar configuración de usuario")
    user_config = ["root", "user_mgmt", "auth", "content", "quizzes"]
    validation = validator.validate_configuration(
        features, relations, constraints, user_config
    )

    if validation.is_valid:
        print(f"   ✅ Configuración de usuario válida")
    else:
        print(f"   ❌ Configuración de usuario inválida")
        print(f"   🔧 Generando alternativa...")
        alternative = generator.complete_partial_configuration(
            features,
            relations,
            constraints,
            {fid: True for fid in user_config},
        )
        if alternative.success:
            print(f"   ✅ Configuración alternativa encontrada")


def run_all_examples():
    """Ejecuta todos los ejemplos."""
    print("\n" + "=" * 60)
    print("🚀 MOTOR DE VALIDACIÓN DE FEATURE MODELS - EJEMPLOS")
    print("=" * 60)

    example_1_validate_model()
    example_2_validate_user_configuration()
    example_3_generate_configurations()
    example_4_complete_partial_configuration()
    example_5_structural_analysis()
    example_6_full_workflow()

    print("\n" + "=" * 60)
    print("✅ TODOS LOS EJEMPLOS COMPLETADOS")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    run_all_examples()
