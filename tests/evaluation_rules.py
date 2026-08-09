from typing import Any, List


VALID_URGENCIES = {"P1", "P2", "P3", "P4"}


def contains_any(text: str, phrases: List[str]) -> bool:
    """Return True when the text contains at least one supplied phrase."""
    normalized = text.lower()
    return any(
        phrase.lower() in normalized
        for phrase in phrases
    )


def validate_required_text(
    value: str,
    required_phrases: List[str],
) -> List[str]:
    """
    Validate that a generated text contains at least one required phrase.

    Returns a list of validation errors.
    """
    if not value or not value.strip():
        return ["Generated text is empty."]

    if required_phrases and not contains_any(
        value,
        required_phrases,
    ):
        return [
            "Generated text does not contain any of the required evidence."
        ]

    return []


def validate_urgency(
    urgency: str,
    expected: str,
) -> List[str]:
    """Validate a Task 1 urgency classification."""
    errors = []

    if urgency not in VALID_URGENCIES:
        errors.append(
            f"Invalid urgency value: {urgency}"
        )
    elif urgency != expected:
        errors.append(
            f"Expected urgency {expected}, got {urgency}."
        )

    return errors


def validate_no_unsupported_claims(
    text: str,
    forbidden_phrases: List[str],
) -> List[str]:
    """
    Detect explicitly forbidden unsupported claims.

    This is intentionally rule-based and conservative.
    """
    errors = []

    normalized = text.lower()

    for phrase in forbidden_phrases:
        if phrase.lower() in normalized:
            errors.append(
                f"Unsupported phrase detected: {phrase}"
            )

    return errors