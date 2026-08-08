from typing import List

from app.models import (
    Account,
    AccountEvidence,
    Ticket,
)

PROMPT_VERSION = "account-summary-v1"


def build_account_summary_prompt(
    account: Account,
    tickets: List[Ticket],
    evidence: List[AccountEvidence],
) -> str:
    """Build the prompt for the final TAM-facing account brief."""

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

    evidence_context = []

    for item in evidence:
        evidence_context.append(
            f"""
SIGNAL: {item.signal}
TYPE: {item.signal_type}
REASON: {item.reason}
SOURCE: {item.source}
TICKET ID: {item.ticket_id}
SUPPORTING QUOTE: {item.supporting_quote}
""".strip()
        )

    evidence_text = "\n\n".join(evidence_context)

    return f"""
You are an account-intelligence assistant preparing a concise
TAM-facing account brief.

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

## VALIDATED ACCOUNT EVIDENCE

The evidence below has already been extracted and validated.
Use it as the primary basis for the account intelligence summary.

{evidence_text}

## INSTRUCTIONS

1. Produce a concise executive summary for a Technical Account Manager.

2. The executive summary must contain 3 to 5 sentences.

3. Summarize the most important account-health, product, escalation,
   and renewal signals supported by the supplied data.

4. Do not invent facts, causes, customer sentiment, business outcomes,
   or future events.

5. Distinguish between account metadata and ticket-derived evidence.

6. Account metadata may be used as factual account context, but must not
   be presented as a direct customer statement.

7. Ticket-derived evidence must remain grounded in the validated
   supporting quote supplied in the evidence section.

8. Do not claim that an issue is resolved unless the supplied data
   explicitly establishes that it is resolved.

9. Do not claim that a support team has investigated, escalated,
   contacted the customer, or taken action unless the supplied data
   explicitly establishes that it happened.

10. Do not convert a possible risk into a certainty.
    For example, a competing-vendor evaluation may indicate churn risk,
    but it does not prove that the customer will churn.

11. The executive summary must describe the account situation, not issue
    unsupported directives or commitments to the TAM.

12. Do not use language such as "the TAM must", "the team will",
    "we will", "the account team should resolve", or similar action
    commitments in the executive summary.

13. If account metadata conflicts with recent ticket history, do not
    silently resolve the contradiction. Describe the discrepancy when
    it is materially relevant.

14. Account escalation notes are metadata and may describe historical
    events that are not present in the supplied recent-ticket data.
    When such information conflicts with the ticket history, do not
    present the metadata statement as a confirmed ticket-history fact.

15. Treat materially different risk signals as separate risks when
    combining them would obscure an important distinction or discrepancy.

16. Produce a "risks" list containing the most important actionable
    risks for the TAM.

17. Each risk must have:
    - a concise title
    - a reason grounded in supplied evidence
    - a supporting quote when the risk is based on ticket evidence

18. Do not fabricate supporting quotes.

19. Produce "talking_points" that are practical points a TAM could use
    when preparing for or conducting a customer conversation.

20. Talking points should be framed as questions, validation areas,
    discussion topics, or relevant follow-up areas grounded in the
    supplied data. They should focus on:
    - issues requiring attention
    - questions worth asking
    - risks worth validating
    - relevant follow-up areas
    - Do not infer customer sentiment from account metadata unless sentiment
    is explicitly stated in the supplied data.

21. Do not invent customer-engagement strategies, remediation plans,
    product fixes, commitments, or business outcomes that are not
    supported by the supplied data.

22. Return ONLY valid JSON matching the required structure.

## REQUIRED JSON STRUCTURE

{{
    "executive_summary": "3 to 5 sentences",
    "risks": [
        {{
            "title": "string",
            "reason": "string",
            "supporting_quote": "string"
        }}
    ],
    "talking_points": [
        "string"
    ]
}}
""".strip()