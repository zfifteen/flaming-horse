import pytest
from harness.util.layout_validator import LayoutValidator
from harness.workflow.config import SCENE_LAYOUT_OPTIONS, LAYOUT_VALIDATION_RULES


def test_layout_validator_valid_layouts():
    """Test that all valid layouts pass validation."""
    validator = LayoutValidator(SCENE_LAYOUT_OPTIONS, LAYOUT_VALIDATION_RULES)
    
    for layout in SCENE_LAYOUT_OPTIONS:
        errors = validator.validate_layout(layout)
        assert errors == [], f"Valid layout '{layout}' should not produce errors, got: {errors}"


def test_layout_validator_invalid_layout():
    """Test that invalid layout tags are rejected."""
    validator = LayoutValidator(SCENE_LAYOUT_OPTIONS, LAYOUT_VALIDATION_RULES)
    
    errors = validator.validate_layout("invalid_layout")
    assert len(errors) > 0, "Invalid layout should produce errors"
    assert "Unknown layout" in errors[0]


def test_layout_validator_get_requirements():
    """Test that layout requirements can be retrieved."""
    validator = LayoutValidator(SCENE_LAYOUT_OPTIONS, LAYOUT_VALIDATION_RULES)
    
    # Test layout with requirements
    reqs = validator.get_layout_requirements("title_card")
    assert isinstance(reqs, list), "Requirements should be a list"
    
    # Test layout without specific requirements (if any exist)
    reqs_empty = validator.get_layout_requirements("full_text")
    assert isinstance(reqs_empty, list), "Requirements should always return a list"


def test_layout_validator_initialization():
    """Test that validator initializes with correct config."""
    validator = LayoutValidator(SCENE_LAYOUT_OPTIONS, LAYOUT_VALIDATION_RULES)
    
    assert validator.valid_layouts == SCENE_LAYOUT_OPTIONS
    assert validator.layout_rules == LAYOUT_VALIDATION_RULES
