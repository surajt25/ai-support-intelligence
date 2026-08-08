from app.data_loader import DataLoader
from app.account_intelligence import AccountContextBuilder
from app.prompts.account_evidence_prompt import (
    build_account_evidence_prompt,
)

loader = DataLoader()

accounts = loader.load_accounts()
tickets = loader.load_tickets()

builder = AccountContextBuilder(
    accounts,
    tickets,
)

account = next(
    account
    for account in accounts
    if account.escalation_notes
)

context = builder.build(account.account_id)

prompt = build_account_evidence_prompt(
    account,
    context.tickets,
)

assert account.company in prompt
assert "RECENT TICKETS" in prompt
assert "supporting_quote" in prompt
assert "ticket_id" in prompt
assert "account_metadata" in prompt
assert "Do not fabricate a supporting quote." in prompt

print("Account evidence prompt test passed.")