r"""
from app.data_loader import DataLoader
from app.prompts.triage_prompt import build_triage_prompt
from app.retrieval import KnowledgeBaseRetriever


loader = DataLoader()

tickets = loader.load_tickets()
documents = loader.load_knowledge_base()

retriever = KnowledgeBaseRetriever()
retriever.build_index(documents)

# Use the CloudSync ticket we already tested.
ticket = tickets[2]

kb_results = retriever.search_ticket(
    ticket,
    top_k=2,
)

prompt = build_triage_prompt(
    ticket,
    kb_results,
)

print(prompt)

"""









from app.data_loader import DataLoader
from app.prompts.triage_prompt import build_triage_prompt
from app.retrieval import KnowledgeBaseRetriever


def test_build_triage_prompt():
    loader = DataLoader()

    tickets = loader.load_tickets()
    documents = loader.load_knowledge_base()

    retriever = KnowledgeBaseRetriever()
    retriever.build_index(documents)

    # Use the CloudSync ticket we have been using for retrieval testing.
    ticket = tickets[2]

    kb_results = retriever.search_ticket(
        ticket,
        top_k=2,
    )

    prompt = build_triage_prompt(
        ticket,
        kb_results,
    )

    # Basic prompt validation.
    assert prompt.strip()

    # Ticket context must be present.
    assert ticket.ticket_id in prompt
    assert ticket.product in prompt
    assert ticket.subject in prompt
    assert ticket.body in prompt

    # Retrieved KB context must be present.
    assert len(kb_results) == 2

    for result in kb_results:
        assert result.document.path in prompt

    # Important: potentially incorrect ticket classifications
    # should not be passed directly to the LLM.
    assert "Category from Ticket: Billing" not in prompt
    assert "Urgency from Ticket: P2" not in prompt

    # Prompt contract must be present.
    assert "triage-v1" in prompt
    assert "Return exactly these fields:" in prompt
    assert '"product_area"' in prompt
    assert '"issue_category"' in prompt
    assert '"urgency"' in prompt
    assert '"matched_kb_document"' in prompt
    assert '"recommended_team"' in prompt
    assert '"draft_response"' in prompt


if __name__ == "__main__":
    test_build_triage_prompt()
    print("Ticket triage prompt test passed.")