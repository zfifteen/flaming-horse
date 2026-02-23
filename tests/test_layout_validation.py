from harness.util.layout_validator import LayoutValidator
from harness.parser import SchemaValidationError, _validate_current_scene_layout


SCENE_LAYOUT_OPTIONS = ["title_card", "full_text", "two_column"]
LAYOUT_VALIDATION_RULES = {
    "title_card": ["title centered", "subtitle directly below title"],
    "two_column": ["left and right columns must not overlap"],
}


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
    """Test that layout requirements are retrieved from configured rules."""
    validator = LayoutValidator(SCENE_LAYOUT_OPTIONS, LAYOUT_VALIDATION_RULES)

    reqs = validator.get_layout_requirements("title_card")
    expected_reqs = LAYOUT_VALIDATION_RULES["title_card"]
    assert isinstance(reqs, list), "Requirements should be a list"
    assert reqs == expected_reqs, "Returned requirements must match configured rules"
    assert len(reqs) > 0, "Layout with configured requirements should not return an empty list"

    reqs_empty = validator.get_layout_requirements("full_text")
    assert isinstance(reqs_empty, list), "Requirements should always return a list"
    assert reqs_empty == [], "Layout without specific requirements should return an empty list"


def test_layout_validator_initialization():
    """Test that validator initializes with correct config."""
    validator = LayoutValidator(SCENE_LAYOUT_OPTIONS, LAYOUT_VALIDATION_RULES)
    assert validator.valid_layouts == set(SCENE_LAYOUT_OPTIONS)
    assert validator.layout_rules == LAYOUT_VALIDATION_RULES


def test_build_scenes_layout_validation_accepts_known_layout():
    scene = {"id": "scene_01", "layout": "title_card"}
    _validate_current_scene_layout(
        scene,
        scene_index=0,
        valid_layouts=SCENE_LAYOUT_OPTIONS,
        layout_rules=LAYOUT_VALIDATION_RULES,
    )


def test_build_scenes_layout_validation_rejects_unknown_layout():
    scene = {"id": "scene_01", "layout": "unknown_layout"}
    try:
        _validate_current_scene_layout(
            scene,
            scene_index=0,
            valid_layouts=SCENE_LAYOUT_OPTIONS,
            layout_rules=LAYOUT_VALIDATION_RULES,
        )
        assert False, "Expected SchemaValidationError for unknown layout"
    except SchemaValidationError as exc:
        assert "valid layout tags" in str(exc)
