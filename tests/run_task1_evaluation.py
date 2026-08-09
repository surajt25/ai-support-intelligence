from app.data_loader import DataLoader
from app.llm import GeminiClient
from app.retrieval import KnowledgeBaseRetriever
from app.triage import TriageService

from tests.evaluate_task1 import evaluate_task1_case
from tests.evaluation_cases import TASK_1_CASES


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

            if errors:
                failed += 1
                print("Result: FAIL")

                for error in errors:
                    print(f"- {error}")
            else:
                passed += 1
                print("Result: PASS")

        except Exception as exc:
            failed += 1
            print("Result: FAIL")
            print(f"- Evaluation execution error: {exc}")

    print("\n=== TASK 1 EVALUATION SUMMARY ===")
    print(f"Total: {len(TASK_1_CASES)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")


if __name__ == "__main__":
    main()