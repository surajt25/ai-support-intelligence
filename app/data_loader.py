import json
from pathlib import Path

from app.config import (
    TICKETS_FILE,
    ACCOUNTS_FILE,
    KB_DIR,
)


class DataLoader:
    """Loads datasets and knowledge base documents"""

    def load_tickets(self):
        
        with open(TICKETS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_accounts(self):
        
        with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_knowledge_base(self):

        kb_documents = []

        for md_file in KB_DIR.rglob("*.md"):
            with open(md_file, "r", encoding="utf-8") as f:
                kb_documents.append(
                    {
                        "file_name": md_file.name,
                        "path": str(md_file.relative_to(KB_DIR)),
                        "content": f.read(),
                    }
                )

        return kb_documents