import json
from typing import List

from app.config import (
    ACCOUNTS_FILE,
    KB_DIR,
    TICKETS_FILE,
)
from app.models import (
    Account,
    KnowledgeBaseDocument,
    Ticket,
)


class DataLoader:
    """Loads datasets and knowledge base documents"""

    def load_tickets(self) -> List[Ticket]:
        """Load and validate support tickets."""

        with open(TICKETS_FILE, "r", encoding="utf-8") as f:
            raw_tickets = json.load(f)

        return [Ticket(**ticket) for ticket in raw_tickets]

    def load_accounts(self) -> List[Account]:
        """Load and validate customer accounts."""

        with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
            raw_accounts = json.load(f)

        return [Account(**account) for account in raw_accounts]

    def load_knowledge_base(self) -> List[KnowledgeBaseDocument]:
        """Load all Markdown knowledge base documents."""

        documents = []

        for md_file in KB_DIR.rglob("*.md"):

            with open(md_file, "r", encoding="utf-8") as f:

                documents.append(
                    KnowledgeBaseDocument(
                        file_name=md_file.name,
                        path=str(md_file.relative_to(KB_DIR)),
                        content=f.read(),
                    )
                )

        return documents