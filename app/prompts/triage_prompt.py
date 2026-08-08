from typing import List

from app.models import SearchResult, Ticket


# Prompt version for traceability and evaluation.
PROMPT_VERSION = "triage-v1"


ALLOWED_RESPONDER_TEAMS = [
    "Analytics Support Team",
    "Integration Support Team",
    "Platform Support Team",
    "Security Support Team",
    "Workflow Automation Team",
    "General Support Team",
]


def build_triage_prompt(
    ticket: Ticket,
    kb_results: List[SearchResult],
) -> str:
    """
    Build the prompt used by the LLM for ticket triage.
    """

    kb_context = []

    for index, result in enumerate(kb_results, start=1):
        kb_context.append(
            f"""
KB DOCUMENT {index}
Path: {result.document.path}
Similarity Score: {result.similarity_score:.3f}

Content:
{result.document.content}
"""
        )

    knowledge_context = "\n".join(kb_context)

    allowed_teams = "\n".join(
        f"- {team}"
        for team in ALLOWED_RESPONDER_TEAMS
    )

    return f"""
You are a support-ticket triage assistant.

Your task is to analyze the provided support ticket and produce
a structured triage decision.

PROMPT VERSION:
{PROMPT_VERSION}

TICKET
------
Ticket ID: {ticket.ticket_id}
Account ID: {ticket.account_id}
Company: {ticket.company}


Product: {ticket.product}
Product Area Metadata: {ticket.product_area}
Status: {ticket.status}


Subject:
{ticket.subject}

Body:
{ticket.body}

KNOWLEDGE BASE CONTEXT
----------------------
{knowledge_context}

RESPONDER TEAM TAXONOMY
----------------------
These are the application's configured responder-team categories.
Do not invent additional team names.

Choose exactly one of the following teams:

{allowed_teams}

INSTRUCTIONS
------------
1. Determine the most appropriate product area based on the actual issue described in the ticket.
2. Determine the issue category based on the actual customer problem, not merely on metadata supplied with the ticket.
3. Determine the urgency as P1, P2, P3, or P4 based on the impact, severity, and evidence in the ticket.
4. Treat the supplied Product Area Metadata as contextual information, not as a guaranteed correct classification.
5. Do not assume an issue is Billing merely because other ticket metadata suggests Billing.
6. Explain the reasoning using evidence from the ticket and, when
   relevant, the retrieved knowledge-base context.
7. Identify the most relevant knowledge-base document based on the actual
   issue and the document content. Do not select a document solely because
   it has the highest retrieval similarity score.
8. Choose exactly one responder team from the allowed team list.
9. Draft a professional first response to the customer.
10. Do not invent product capabilities, policies, fixes, or facts
   that are not supported by the ticket or knowledge-base context.
11. If the knowledge base does not contain a clear answer, say so
   in the reasoning rather than inventing one.
12. Return ONLY valid JSON matching the requested output structure.
13. The urgency value MUST be exactly one of: "P1", "P2", "P3", or "P4".
14. The recommended_team value MUST be exactly one of the responder teams listed above.

## REQUIRED JSON STRUCTURE

Return exactly these fields:

{{
"product_area": "string",
"issue_category": "string",
"urgency": "P1",
"reasoning": "string",
"matched_kb_document": "string",
"recommended_team": "string",
"draft_response": "string"
}}

The "urgency" field must contain exactly one of:
"P1", "P2", "P3", or "P4".

The "recommended_team" field must contain exactly one of the
responder teams listed above.

The "matched_kb_document" field must contain the path of the
selected document exactly as provided in the knowledge-base context.

""".strip()