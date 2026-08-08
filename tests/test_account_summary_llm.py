from app.account_intelligence import (
    AccountContextBuilder,
    validate_account_evidence,
)
from app.data_loader import DataLoader
from app.llm import GeminiClient
from app.prompts.account_evidence_prompt import (
    build_account_evidence_prompt,
)
from app.prompts.account_summary_prompt import (
    build_account_summary_prompt,
)


def test_account_summary_llm():
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

    client = GeminiClient()

    # Stage 1: extract evidence.
    evidence_prompt = build_account_evidence_prompt(
        account,
        context.tickets,
    )

    evidence_response = client.generate_account_evidence(
        evidence_prompt
    )

    # Validate evidence before synthesis.
    validate_account_evidence(
        evidence_response,
        context.tickets,
    )

    # Stage 2: generate final TAM summary.
    summary_prompt = build_account_summary_prompt(
        account,
        context.tickets,
        evidence_response.evidence,
    )

    result = client.generate_account_summary(
        summary_prompt
    )

    print("\n# Account Intelligence Summary\n")

    print("## Executive Summary")
    print(result.executive_summary)

    print("\n## Risks")

    for risk in result.risks:
        print(f"\nTitle: {risk.title}")
        print(f"Reason: {risk.reason}")
        print(f"Supporting Quote: {risk.supporting_quote}")

    print("\n## Talking Points")

    for point in result.talking_points:
        print(f"- {point}")


if __name__ == "__main__":
    test_account_summary_llm()