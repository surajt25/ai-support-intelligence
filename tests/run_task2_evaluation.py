import json
from pathlib import Path

from app.account_intelligence import (
    AccountContextBuilder,
    AccountIntelligenceService,
)
from app.data_loader import DataLoader
from app.llm import GeminiClient

from tests.evaluate_task2 import evaluate_task2_case
from tests.evaluation_cases import TASK_2_CASES


def calculate_quality_score(errors):
    """Convert validation errors into a deterministic 0-1 score."""

    if not errors:
        return 1.0

    return max(
        0.0,
        round(1.0 - (0.2 * len(errors)), 2),
    )


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
    scores = []

    report = {
        "task": "task2",
        "total": len(TASK_2_CASES),
        "passed": 0,
        "failed": 0,
        "average_quality_score": 0.0,
        "cases": [],
    }

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

            quality_score = calculate_quality_score(errors)
            scores.append(quality_score)

            if errors:
                failed += 1
                print("\nResult: FAIL")

                for error in errors:
                    print(f"- {error}")

            else:
                passed += 1
                print("\nResult: PASS")

            print(f"Quality Score: {quality_score:.2f}")

            report["cases"].append(
                {
                    "case_id": case.case_id,
                    "input_id": case.input_id,
                    "passed": not errors,
                    "quality_score": quality_score,
                    "errors": errors,
                }
            )


        except Exception as exc:
            failed += 1
            scores.append(0.0)

            print("\nResult: FAIL")
            print(
                f"- Evaluation execution error: {exc}"
            )
            print("Quality Score: 0.00")


    print(
        "\n=== TASK 2 EVALUATION SUMMARY ==="
    )
    print(f"Total: {len(TASK_2_CASES)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    average_score = (
        sum(scores) / len(scores)
        if scores
        else 0.0
    )

    print(f"Average Quality Score: {average_score:.2f}")

    report["passed"] = passed
    report["failed"] = failed
    report["average_quality_score"] = round(
        average_score,
        2,
    )

    report_path = Path("eval_report_task2.json")

    with report_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            report,
            file,
            indent=2,
        )

    print(f"Evaluation report written to {report_path}")


if __name__ == "__main__":
    main()
