from app.account_intelligence import (
    AccountContextBuilder,
    AccountIntelligenceService,
)
from app.data_loader import DataLoader
from app.llm import GeminiClient

from tests.evaluate_task2 import evaluate_task2_case
from tests.evaluation_cases import TASK_2_CASES


def main():
    loader = DataLoader()

    accounts = loader.load_accounts()
    tickets = loader.load_tickets()

    context_builder = AccountContextBuilder(
        accounts,
        tickets,
    )

    llm_client = GeminiClient()

    service = AccountIntelligenceService(
        context_builder=context_builder,
        llm_client=llm_client,
    )

    passed = 0
    failed = 0

    for case in TASK_2_CASES:
        account = next(
            (
                account
                for account in accounts
                if account.account_id == case.input_id
            ),
            None,
        )

        if account is None:
            print(f"{case.case_id}: FAIL")
            print(
                f"  Account not found: {case.input_id}"
            )
            failed += 1
            continue

        context = context_builder.build(
            account.account_id
        )

        if context is None:
            print(f"{case.case_id}: FAIL")
            print(
                f"  Could not build context for "
                f"{account.account_id}"
            )
            failed += 1
            continue

        print(f"\n=== {case.case_id} ===")
        print(f"Input: {account.account_id}")
        print(f"Company: {account.company}")

        try:
            result = service.analyze(
                account.account_id
            )

            print(
                f"Health: {account.health_status}"
            )
            print(
                f"Usage: {account.usage_trend}"
            )
            print(
                f"Tickets in 90d: "
                f"{len(context.tickets)}"
            )

            print(
                "\nExecutive Summary:"
            )
            print(
                result.executive_summary
            )

            print("\nRisks:")

            for risk in result.risks:
                print(
                    f"- {risk.title}"
                )
                print(
                    f"  Reason: {risk.reason}"
                )
                print(
                    f"  Quote: "
                    f"{risk.supporting_quote}"
                )
                print(
                    f"  Source: {risk.source}"
                )
                print(
                    f"  Ticket: "
                    f"{risk.ticket_id}"
                )

            print("\nTalking Points:")

            for point in result.talking_points:
                print(
                    f"- {point}"
                )

            errors = evaluate_task2_case(
                case=case,
                account=account,
                tickets=context.tickets,
                result=result,
            )

            if errors:
                failed += 1
                print("\nResult: FAIL")

                for error in errors:
                    print(f"- {error}")

            else:
                passed += 1
                print("\nResult: PASS")

        except Exception as exc:
            failed += 1
            print("\nResult: FAIL")
            print(
                f"- Evaluation execution error: {exc}"
            )

    print(
        "\n=== TASK 2 EVALUATION SUMMARY ==="
    )
    print(f"Total: {len(TASK_2_CASES)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")


if __name__ == "__main__":
    main()