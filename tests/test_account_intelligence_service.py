from app.account_intelligence import (
    AccountContextBuilder,
    AccountIntelligenceService,
)
from app.data_loader import DataLoader
from app.llm import GeminiClient


def test_account_intelligence_service():
    loader = DataLoader()

    accounts = loader.load_accounts()
    tickets = loader.load_tickets()

    context_builder = AccountContextBuilder(
        accounts,
        tickets,
    )

    account = next(
        account
        for account in accounts
        if account.escalation_notes
    )

    llm_client = GeminiClient()

    service = AccountIntelligenceService(
        context_builder=context_builder,
        llm_client=llm_client,
    )

    result = service.analyze(account.account_id)

    print("\n# Account Intelligence Service Result\n")
    print("Executive Summary:")
    print(result.executive_summary)

    print("\nRisks:")
    for risk in result.risks:
        print(f"\nTitle: {risk.title}")
        print(f"Reason: {risk.reason}")
        print(f"Supporting Quote: {risk.supporting_quote}")

    print("\nTalking Points:")
    for point in result.talking_points:
        print(f"- {point}")

    assert result.executive_summary
    assert 3 <= len(
        [
            sentence
            for sentence in result.executive_summary.split(".")
            if sentence.strip()
        ]
    ) <= 5

    assert result.risks
    assert result.talking_points

    performance_risk = next(
        (
            risk
            for risk in result.risks
            if "DataBridge" in risk.title
        ),
        None,
    )

    assert performance_risk is not None

    ticket_text = [
        f"{ticket.subject}\n{ticket.body}"
        for ticket in tickets
    ]

    assert any(
        performance_risk.supporting_quote in text
        for text in ticket_text
    )


if __name__ == "__main__":
    test_account_intelligence_service()
    print("\nAccount intelligence service test passed.")