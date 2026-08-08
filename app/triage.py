from typing import List

from app.config import TOP_K_DOCUMENTS
from app.llm import GeminiClient
from app.models import SearchResult, Ticket, TriageResponse
from app.prompts.triage_prompt import build_triage_prompt
from app.retrieval import KnowledgeBaseRetriever


class TriageService:
    """Orchestrates retrieval, prompt construction, and LLM triage."""

    def __init__(
        self,
        retriever: KnowledgeBaseRetriever,
        llm_client: GeminiClient,
        top_k: int = TOP_K_DOCUMENTS,
    ):
        self.retriever = retriever
        self.llm_client = llm_client
        self.top_k = top_k

    def triage(self, ticket: Ticket) -> TriageResponse:
        """
        Perform end-to-end triage for a single support ticket.
        """

        kb_results: List[SearchResult] = self.retriever.search_ticket(
            ticket,
            top_k=self.top_k,
        )

        prompt = build_triage_prompt(
            ticket,
            kb_results,
        )

        return self.llm_client.generate_triage(prompt)