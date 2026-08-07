from app.data_loader import DataLoader

loader = DataLoader()

tickets = loader.load_tickets()
accounts = loader.load_accounts()
kb_docs = loader.load_knowledge_base()

print(f"Tickets: {len(tickets)}")
print(f"Accounts: {len(accounts)}")
print(f"KB Docs: {len(kb_docs)}")

print("\nFirst Ticket Type:")
print(type(tickets[0]))

print("\nFirst Account Type:")
print(type(accounts[0]))

print("\nFirst KB Document Type:")
print(type(kb_docs[0]))

print("\nFirst Ticket Subject:")
print(tickets[0].subject)

print("\nFirst Account Company:")
print(accounts[0].company)

print("\nFirst KB File:")
print(kb_docs[0].file_name)