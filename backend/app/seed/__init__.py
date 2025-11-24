"""
Módulo centralizado de seeding de base de datos

Este módulo contiene todos los datos de ejemplo y funciones de seeding
organizados de manera modular y reutilizable.
"""

from .main import seed_all, seed_production, seed_development
from .seeders import (
    create_first_superuser,
    seed_settings,
    seed_production_users,
    seed_development_users,
    seed_domains,
    seed_tags,
    seed_resources,
    seed_feature_models,
    get_admin_user,
)

__all__ = [
    "seed_all",
    "seed_production",
    "seed_development",
    "create_first_superuser",
    "seed_settings",
    "seed_production_users",
    "seed_development_users",
    "seed_domains",
    "seed_tags",
    "seed_resources",
    "seed_feature_models",
    "get_admin_user",
]
