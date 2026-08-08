from app.models import (
    KnowledgeBaseDocument,
    SearchResult,
    Ticket,
    TriageResponse,
)
from app.triage import TriageService


class FakeRetriever:
    """Fake KB retriever for unit testing."""

    def search_ticket(self, ticket, top_k=3):
        document = KnowledgeBaseDocument(
            file_name="cloudsync.md",
            path="products/cloudsync.md",
            content="CloudSync webhook troubleshooting information.",
        )

        return [
            SearchResult(
                document=document,
                similarity_score=0.9,
            )
        ]


class FakeLLMClient:
    """Fake LLM client for unit testing."""

    def generate_triage(self, prompt):
        assert "CloudSync" in prompt

        return TriageResponse(
            product_area="Integrations",
            issue_category="Webhook Delivery Failure",
            urgency="P2",
            reasoning="Test reasoning.",
            matched_kb_document="products/cloudsync.md",
            recommended_team="Integration Support Team",
            draft_response="Test response.",
        )


def test_triage_service():
    ticket = Ticket(
        ticket_id="TKT-TEST",
        account_id="ACC-TEST",
        company="Test Company",
        subject="CloudSync webhook failure",
        body="Webhook deliveries are failing.",
        product="CloudSync",
        product_area="Conflict Resolution",
        category="Billing",
        urgency="P2",
        status="Open",
        plan_tier="Business",
        assigned_agent="Test Agent",
        created_at="2026-01-01T00:00:00Z",
        updated_at="2026-01-01T00:00:00Z",
        tags=[],
        channel="portal",
        satisfaction_score=None,
    )

    service = TriageService(
        retriever=FakeRetriever(),
        llm_client=FakeLLMClient(),
    )

    result = service.triage(ticket)

    assert isinstance(result, TriageResponse)
    assert result.product_area == "Integrations"
    assert result.issue_category == "Webhook Delivery Failure"
    assert result.urgency == "P2"
    assert result.recommended_team == "Integration Support Team"


if __name__ == "__main__":
    test_triage_service()
    print("Triage service test passed.")