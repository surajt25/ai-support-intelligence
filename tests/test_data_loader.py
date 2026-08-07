from app.data_loader import DataLoader

loader = DataLoader()

tickets = loader.load_tickets()
accounts = loader.load_accounts()
kb_docs = loader.load_knowledge_base()

print(f"Tickets: {len(tickets)}")
print(f"Accounts: {len(accounts)}")
print(f"KB Docs: {len(kb_docs)}")