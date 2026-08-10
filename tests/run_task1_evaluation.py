import json
from pathlib import Path

from app.data_loader import DataLoader
from app.llm import GeminiClient
from app.retrieval import KnowledgeBaseRetriever
from app.triage import TriageService

from tests.evaluate_task1 import evaluate_task1_case
from tests.evaluation_cases import TASK_1_CASES


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

    tickets = loader.load_tickets()
    documents = loader.load_knowledge_base()

    retriever = KnowledgeBaseRetriever()
    retriever.build_index(documents)

    llm_client = GeminiClient()

    service = TriageService(
        retriever=retriever,
        llm_client=llm_client,
    )

    passed = 0
    failed = 0
    scores = []

    report = {
        "task": "task1",
        "total": len(TASK_1_CASES),
        "passed": 0,
        "failed": 0,
        "average_quality_score": 0.0,
        "cases": [],
    }

    for case in TASK_1_CASES:
        ticket = next(
            (
                ticket
                for ticket in tickets
                if ticket.ticket_id == case.input_id
            ),
            None,
        )

        if ticket is None:
            print(f"{case.case_id}: FAIL")
            print(f"  Ticket not found: {case.input_id}")
            failed += 1
            continue

        print(f"\n=== {case.case_id} ===")
        print(f"Input: {ticket.ticket_id}")
        print(f"Subject: {ticket.subject}")

        try:
            result = service.triage(ticket)

            print(f"Product Area: {result.product_area}")
            print(f"Issue Category: {result.issue_category}")
            print(f"Urgency: {result.urgency}")
            print(f"Matched KB: {result.matched_kb_document}")
            print(f"Recommended Team: {result.recommended_team}")
            print(f"Reasoning: {result.reasoning}")

            errors = evaluate_task1_case(
                case=case,
                ticket=ticket,
                result=result,
            )

            quality_score = calculate_quality_score(errors)
            scores.append(quality_score)

            if errors:
                failed += 1
                print("Result: FAIL")

                for error in errors:
                    print(f"- {error}")
            else:
                passed += 1
                print("Result: PASS")

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

            print("Result: FAIL")
            print(f"- Evaluation execution error: {exc}")
            print("Quality Score: 0.00")


    print("\n=== TASK 1 EVALUATION SUMMARY ===")
    print(f"Total: {len(TASK_1_CASES)}")
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

    report_path = Path("eval_report_task1.json")

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
