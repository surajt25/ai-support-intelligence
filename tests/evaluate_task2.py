from typing import List

from app.models import Account, AccountSummary, Ticket

from tests.evaluation_cases import EvaluationCase
from tests.evaluation_rules import (
    contains_any,
    validate_account_metadata_presence,
    validate_no_unsupported_claims,
    validate_ticket_reference,
)


FORBIDDEN_ACCOUNT_CLAIMS = [
    "we have investigated",
    "we investigated",
    "our team investigated",
    "we have escalated",
    "we escalated",
    "our team escalated",
    "we have resolved",
    "we resolved",
    "the issue has been resolved",
    "the customer will churn",
    "the customer is going to churn",
]


def _all_generated_text(result: AccountSummary) -> str:
    """Combine all generated fields for deterministic validation."""

    risk_text = []

    for risk in result.risks:
        risk_text.append(
            risk.title
        )
        risk_text.append(
            risk.reason
        )
        risk_text.append(
            risk.supporting_quote
        )

    return "\n".join(
        [
            result.executive_summary,
            *risk_text,
            *result.talking_points,
        ]
    )


def _validate_summary_length(
    executive_summary: str,
) -> List[str]:
    """Validate the required 3–5 sentence executive summary."""

    sentences = [
        sentence.strip()
        for sentence in executive_summary.split(".")
        if sentence.strip()
    ]

    if not 3 <= len(sentences) <= 5:
        return [
            "Executive summary must contain between "
            "3 and 5 sentences."
        ]

    return []


def _validate_ticket_quote(
    quote: str,
    ticket: Ticket,
) -> List[str]:
    """Validate that a supporting quote exists in the actual ticket."""

    if not quote.strip():
        return [
            f"Risk based on {ticket.ticket_id} "
            "has an empty supporting quote."
        ]

    if (
        quote not in ticket.subject
        and quote not in ticket.body
    ):
        return [
            f"Supporting quote for {ticket.ticket_id} "
            "was not found in the supplied ticket."
        ]

    return []


def evaluate_task2_case(
    case: EvaluationCase,
    account: Account,
    tickets: List[Ticket],
    result: AccountSummary,
) -> List[str]:
    """
    Evaluate a single Task 2 account-intelligence result.

    Returns a list of validation errors.
    An empty list means the deterministic checks passed.
    """

    errors: List[str] = []

    generated_text = _all_generated_text(result)

    # ---------------------------------------------------------
    # Basic output validation
    # ---------------------------------------------------------

    if not result.executive_summary.strip():
        errors.append("Executive summary is empty.")

    errors.extend(
        _validate_summary_length(
            result.executive_summary
        )
    )

    if not result.risks:
        errors.append("Risks list is empty.")

    if not result.talking_points:
        errors.append("Talking points list is empty.")

    # ---------------------------------------------------------
    # Account metadata grounding
    # ---------------------------------------------------------

    errors.extend(
        validate_account_metadata_presence(
            generated_text,
            account.health_status,
            account.usage_trend,
        )
    )

    # ---------------------------------------------------------
    # Unsupported-action / fabricated-claim checks
    # ---------------------------------------------------------

    errors.extend(
        validate_no_unsupported_claims(
            generated_text,
            FORBIDDEN_ACCOUNT_CLAIMS,
        )
    )

    # ---------------------------------------------------------
    # Ticket-derived evidence validation
    # ---------------------------------------------------------

    available_ticket_ids = {
        ticket.ticket_id
        for ticket in tickets
    }

    for risk in result.risks:
        if risk.ticket_id:
            if risk.ticket_id not in available_ticket_ids:
                errors.append(
                    f"Risk references unavailable ticket "
                    f"{risk.ticket_id}."
                )
                continue

            ticket = next(
                ticket
                for ticket in tickets
                if ticket.ticket_id == risk.ticket_id
            )

            errors.extend(
                validate_ticket_reference(
                    generated_text,
                    ticket.ticket_id,
                )
            )

            errors.extend(
                _validate_ticket_quote(
                    risk.supporting_quote,
                    ticket,
                )
            )

    # ---------------------------------------------------------
    # Prevent unsupported customer sentiment
    # ---------------------------------------------------------

    if not account.escalation_notes:
        sentiment_phrases = [
            "customer is frustrated",
            "customer was frustrated",
            "negative sentiment",
            "customer dissatisfaction",
            "customer is dissatisfied",
        ]

        if contains_any(
            generated_text,
            sentiment_phrases,
        ):
            errors.append(
                "Generated customer sentiment without "
                "supporting account metadata."
            )

    return errors