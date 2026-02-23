from typing import Dict, Iterable, List, Mapping


class LayoutValidator:
    """
    Validates scene layout tags against defined options and requirements.
    """

    def __init__(
        self,
        valid_layouts: Iterable[str],
        layout_rules: Mapping[str, List[str]],
    ):
        """
        Args:
            valid_layouts: Set of valid layout tag strings
            layout_rules: Dict mapping layout tags to lists of requirement strings
        """
        self.valid_layouts = set(valid_layouts)
        self.layout_rules: Dict[str, List[str]] = {
            key: list(value) for key, value in layout_rules.items()
        }

    def validate_layout(self, layout: str) -> List[str]:
        """
        Validate a layout tag against defined rules.

        Args:
            layout: Layout tag string to validate

        Returns:
            List of error messages. Empty list means valid.
        """
        errors = []

        # Check if layout is in valid set
        if layout not in self.valid_layouts:
            errors.append(
                f"Unknown layout '{layout}'. Valid layouts: {', '.join(sorted(self.valid_layouts))}"
            )
            return errors

        return errors

    def get_layout_requirements(self, layout: str) -> List[str]:
        """
        Get requirement list for a specific layout.

        Args:
            layout: Layout tag string

        Returns:
            List of requirement strings, or empty list if layout has no specific requirements
        """
        return self.layout_rules.get(layout, [])
