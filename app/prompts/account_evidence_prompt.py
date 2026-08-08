from app.models import Account, Ticket

PROMPT_VERSION = "account-evidence-v1"

def build_account_evidence_prompt(
    account: Account,
    tickets: list[Ticket],
) -> str:
    ticket_context = []

    for ticket in tickets:
        ticket_context.append(
            f"""
TICKET
ID: {ticket.ticket_id}
Status: {ticket.status}
Urgency: {ticket.urgency}
Product: {ticket.product}
Product Area: {ticket.product_area}
Category: {ticket.category}

Subject:
{ticket.subject}

Body:
{ticket.body}
""".strip()
        )

    tickets_text = "\n\n".join(ticket_context)

    return f"""
You are an account-intelligence evidence extraction assistant.

Your task is to identify evidence relevant to customer health,
churn risk, escalation risk, and important account issues.

PROMPT VERSION:
{PROMPT_VERSION}

## ACCOUNT

Account ID: {account.account_id}
Company: {account.company}
Health Status: {account.health_status}
Usage Trend: {account.usage_trend}
ARR: {account.arr_usd}
Licensed Seats: {account.seats_licensed}
Active Seats: {account.seats_active}
Open Tickets: {account.open_tickets}
P1 Tickets Last 30 Days: {account.p1_tickets_last_30d}
Renewal Date: {account.renewal_date}
NPS Score: {account.nps_score}

Account Escalation Notes:
{account.escalation_notes}

## RECENT TICKETS

{tickets_text}

## INSTRUCTIONS

1. Extract only evidence supported by the supplied account data or tickets.

2. Identify meaningful signals related to:
   - churn risk
   - escalation risk
   - product or service problems
   - customer dissatisfaction
   - account health
   - renewal risk

3. Do not invent facts, events, customer sentiment, or causes.

4. If a signal comes from a ticket, the supporting_quote MUST be
   copied directly from that ticket's subject or body.

5. Do not fabricate a supporting quote.

6. If a signal comes only from account metadata, set:
   - source = "account_metadata"
   - supporting_quote = ""

7. If a signal comes from a ticket, set:
    - source = "ticket"
    - ticket_id = the ID of the ticket providing the evidence
    - supporting_quote = an exact substring copied from that ticket's subject or body.

8. If a signal comes only from account metadata, set:
    - source = "account_metadata"
    - ticket_id = null
    - supporting_quote = ""

8. Account escalation notes are account metadata. They must not be
   presented as ticket evidence.

9. Do not treat an account metadata statement as independently
   verified by the ticket history.

10. If account metadata conflicts with the supplied ticket history,
    preserve the discrepancy rather than resolving it by assumption.

11. Avoid creating multiple signals that express the same underlying issue.

12. Return ONLY valid JSON matching the required structure.

## REQUIRED JSON STRUCTURE

{{
    "evidence": [
        {{
            "signal": "string",
            "signal_type": "string",
            "reason": "string",
            "supporting_quote": "string",
            "source": "ticket | account_metadata",
            "ticket_id": "string | null"
        }}
    ]
}}
""".strip()