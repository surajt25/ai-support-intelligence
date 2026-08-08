from typing import List

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.config import SIMILARITY_THRESHOLD
from app.models import (
    KnowledgeBaseDocument,
    SearchResult,
    Ticket,
)


class KnowledgeBaseRetriever:
    """Retrieves the most relevant knowledge base documents."""

    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            lowercase=True,
            ngram_range=(1, 2),
            sublinear_tf=True,
        )

        self.documents: List[KnowledgeBaseDocument] = []
        self.document_matrix = None

    def build_index(
        self,
        documents: List[KnowledgeBaseDocument],
    ) -> None:
        """Create TF-IDF vectors for all KB documents."""

        self.documents = documents

        corpus = [
            f"{doc.file_name} {doc.path} {doc.content}"
            for doc in documents
        ]

        self.document_matrix = self.vectorizer.fit_transform(corpus)

    def search(
        self,
        query: str,
        top_k: int = 3,
    ) -> List[SearchResult]:
        """Return the top matching KB documents."""

        if self.document_matrix is None:
            raise RuntimeError(
                "Knowledge base index has not been built."
            )

        query = query.lower()

        query_vector = self.vectorizer.transform([query])

        similarities = cosine_similarity(
            query_vector,
            self.document_matrix,
        ).flatten()

        ranked_indices = similarities.argsort()[::-1][:top_k]

        results = []

        for index in ranked_indices:
            score = float(similarities[index])

            # Ignore very weak matches.
            if score < SIMILARITY_THRESHOLD:
                continue

            results.append(
                SearchResult(
                    document=self.documents[index],
                    similarity_score=score,
                )
            )

        return results

    def search_ticket(
        self,
        ticket: Ticket,
        top_k: int = 3,
    ) -> List[SearchResult]:
        """Search the KB using the complete ticket context."""

        query = " ".join(
            [
                ticket.product,
                ticket.product_area,
                ticket.subject,
                ticket.body,
            ]
        )

        return self.search(query, top_k)