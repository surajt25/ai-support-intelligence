from app.account_intelligence import AccountContextBuilder
from app.data_loader import DataLoader
from app.models import AccountEvidence
from app.prompts.account_summary_prompt import (
    build_account_summary_prompt,
)


def test_account_summary_prompt():
    loader = DataLoader()

    accounts = loader.load_accounts()
    tickets = loader.load_tickets()

    builder = AccountContextBuilder(
        accounts,
        tickets,
    )

    account = next(
        account
        for account in accounts
        if account.escalation_notes
    )

    context = builder.build(account.account_id)

    if context is None:
        raise RuntimeError(
            "Failed to build account context."
        )

    evidence = [
        AccountEvidence(
            signal="Severe DataBridge Pro performance degradation",
            signal_type="product_or_service_problem",
            reason="The ticket reports severe performance degradation.",
            supporting_quote=(
                "We've noticed significant performance degradation "
                "in DataBridge Pro over the past 12 days."
            ),
            source="ticket",
            ticket_id="TKT-10293",
        ),
        AccountEvidence(
            signal="Account is at risk",
            signal_type="churn_risk",
            reason="Account metadata marks the account as At Risk.",
            supporting_quote="",
            source="account_metadata",
            ticket_id=None,
        ),
    ]

    prompt = build_account_summary_prompt(
        account,
        context.tickets,
        evidence,
    )

    assert account.company in prompt
    assert "VALIDATED ACCOUNT EVIDENCE" in prompt
    assert "executive_summary" in prompt
    assert "risks" in prompt
    assert "talking_points" in prompt
    assert "3 to 5 sentences" in prompt
    assert "Do not fabricate supporting quotes." in prompt
    assert "TKT-10293" in prompt

    print("Account summary prompt test passed.")


if __name__ == "__main__":
    test_account_summary_prompt()