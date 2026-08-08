from app.account_intelligence import (
    AccountContextBuilder,
    validate_account_evidence,
)
from app.data_loader import DataLoader
from app.llm import GeminiClient
from app.prompts.account_evidence_prompt import (
    build_account_evidence_prompt,
)


def test_account_evidence_llm():
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

    prompt = build_account_evidence_prompt(
        account,
        context.tickets,
    )

    client = GeminiClient()

    result = client.generate_account_evidence(
        prompt
    )

    validate_account_evidence(
        result,
        context.tickets,
    )

    print("\n# Account Evidence\n")

    for evidence in result.evidence:
        print("Signal:", evidence.signal)
        print("Type:", evidence.signal_type)
        print("Reason:", evidence.reason)
        print("Source:", evidence.source)
        print("Quote:", evidence.supporting_quote)
        print()


if __name__ == "__main__":
    test_account_evidence_llm()