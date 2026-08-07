from typing import List, Optional

from pydantic import BaseModel


# INPUT DATA MODELS
class PrimaryContact(BaseModel):
    name: str
    title: str


class Ticket(BaseModel):
    ticket_id: str
    account_id: str
    company: str

    subject: str
    body: str

    product: str
    product_area: str
    category: str
    urgency: str
    status: str

    plan_tier: str
    assigned_agent: str

    created_at: str
    updated_at: str

    tags: List[str]

    channel: str
    satisfaction_score: Optional[int]


class Account(BaseModel):
    account_id: str
    company: str

    tam: str

    plan_tier: str

    arr_usd: int

    seats_licensed: int
    seats_active: int

    products: List[str]

    health_status: str
    usage_trend: str

    open_tickets: int
    p1_tickets_last_30d: int

    customer_since: str
    renewal_date: str
    last_qbr_date: str

    primary_contact: PrimaryContact

    escalation_notes: List[str]

    nps_score: Optional[int]

    last_login_days_ago: int

    integrations_active: List[str]

    region: str
    industry: str



# KNOWLEDGE BASE MODEL
class KnowledgeBaseDocument(BaseModel):
    file_name: str
    path: str
    content: str


# TASK 1 OUTPUT
class TriageResponse(BaseModel):
    product_area: str
    issue_category: str
    urgency: str

    reasoning: str

    matched_kb_document: str

    recommended_team: str

    draft_response: str



# TASK 2 OUTPUT
class RiskFlag(BaseModel):
    title: str
    reason: str
    supporting_quote: str


class AccountSummary(BaseModel):
    executive_summary: str

    risks: List[RiskFlag]

    talking_points: List[str]