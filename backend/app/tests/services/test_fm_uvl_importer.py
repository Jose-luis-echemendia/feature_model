import pytest

from app.services.feature_model.fm_uvl_importer import (
    FeatureModelUVLImporter,
    UVLParseError,
)


VALID_UVL = """namespace Test

features
    Root
        optional
            Child

constraints
    Root => Child
"""

INVALID_INDENT_UVL = """features
  Root
    Child
"""


def test_validate_uvl_only_success():
    result = FeatureModelUVLImporter.validate_uvl_only(VALID_UVL)

    assert result["is_valid"] is True
    assert result["root"] == "Root"
    assert result["features"] == 2
    assert result["constraints"] == 1


def test_validate_uvl_only_invalid_indentation():
    with pytest.raises(UVLParseError):
        FeatureModelUVLImporter.validate_uvl_only(INVALID_INDENT_UVL)
