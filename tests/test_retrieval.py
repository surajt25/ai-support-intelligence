from app.data_loader import DataLoader
from app.retrieval import KnowledgeBaseRetriever

loader = DataLoader()

tickets = loader.load_tickets()

documents = loader.load_knowledge_base()

retriever = KnowledgeBaseRetriever()

retriever.build_index(documents)

ticket = tickets[2]

print("=" * 60)
print(ticket.subject)
print("=" * 60)

results = retriever.search_ticket(ticket)

print()

for result in results:
    print(
        f"{result.similarity_score:.3f}"
        f"    {result.document.path}"
    )