from app.data_loader import DataLoader
from app.llm import GeminiClient
from app.prompts.triage_prompt import build_triage_prompt
from app.retrieval import KnowledgeBaseRetriever
from app.models import TriageResponse


def test_real_gemini_triage():
    loader = DataLoader()

    tickets = loader.load_tickets()
    documents = loader.load_knowledge_base()

    # Use the same CloudSync ticket we've been testing.
    ticket = tickets[2]

    retriever = KnowledgeBaseRetriever()
    retriever.build_index(documents)

    kb_results = retriever.search_ticket(
        ticket,
        top_k=2,
    )

    prompt = build_triage_prompt(
        ticket,
        kb_results,
    )

    client = GeminiClient()

    result = client.generate_triage(prompt)

    assert isinstance(result, TriageResponse)

    print("\nGemini Triage Result")
    print("====================")
    print(f"Product Area: {result.product_area}")
    print(f"Issue Category: {result.issue_category}")
    print(f"Urgency: {result.urgency}")
    print(f"Matched KB: {result.matched_kb_document}")
    print(f"Recommended Team: {result.recommended_team}")
    print(f"\nReasoning:\n{result.reasoning}")
    print(f"\nDraft Response:\n{result.draft_response}")


if __name__ == "__main__":
    test_real_gemini_triage()