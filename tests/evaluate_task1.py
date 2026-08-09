from typing import List

from app.models import Ticket, TriageResponse

from tests.evaluation_cases import EvaluationCase
from tests.evaluation_rules import (
    validate_no_unsupported_claims,
    validate_urgency,
)


FORBIDDEN_TRIAGE_CLAIMS = [
    "we have investigated",
    "we investigated",
    "our team investigated",
    "we have escalated",
    "we escalated",
    "our team escalated",
    "we have resolved",
    "we resolved",
    "the issue has been resolved",
]


def evaluate_task1_case(
    case: EvaluationCase,
    ticket: Ticket,
    result: TriageResponse,
) -> List[str]:
    """
    Evaluate a single Task 1 triage result.

    Returns a list of validation errors.
    An empty list means the deterministic checks passed.
    """

    errors = []

    # Every Task 1 result must preserve the ticket urgency.
    errors.extend(
        validate_urgency(
            result.urgency,
            ticket.urgency,
        )
    )

    # Combine generated reasoning and draft response because
    # unsupported claims may appear in either field.
    generated_text = "\n".join(
        [
            result.reasoning,
            result.draft_response,
        ]
    )

    errors.extend(
        validate_no_unsupported_claims(
            generated_text,
            FORBIDDEN_TRIAGE_CLAIMS,
        )
    )

    # The generated response should not be empty.
    if not result.reasoning.strip():
        errors.append("Reasoning is empty.")

    if not result.draft_response.strip():
        errors.append("Draft response is empty.")

    if not result.matched_kb_document.strip():
        errors.append("Matched KB document is empty.")

    # The recommended team must be populated.
    if not result.recommended_team.strip():
        errors.append("Recommended team is empty.")

    # Product area and issue category are required structured fields.
    if not result.product_area.strip():
        errors.append("Product area is empty.")

    if not result.issue_category.strip():
        errors.append("Issue category is empty.")

    return errors