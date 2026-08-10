from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class EvaluationCase:
    """Definition of a single evaluation-harness test case."""

    case_id: str
    task: str
    description: str
    input_id: str
    acceptance_criteria: List[str]
    adversarial: bool = False


TASK_1_CASES = [
    EvaluationCase(
        case_id="T1-01",
        task="task1",
        description=(
            "DataBridge Pro performance degradation and API timeout "
            "regression case."
        ),
        input_id="TKT-10293",
        acceptance_criteria=[
            "Urgency must be P2.",
            "The classification must reflect the actual performance/API issue.",
            "Reasoning must reference the reported 119+ second page loads "
            "or API timeouts.",
            "The response must not invent a confirmed root cause.",
            "The matched KB document must be grounded in the retrieved KB context.",
            "The draft response must not claim that the issue was investigated "
            "or resolved merely because the ticket status is Closed.",
        ],
    ),
    EvaluationCase(
        case_id="T1-02",
        task="task1",
        description=(
            "WorkflowEngine P1 error and insufficient-scope access case."
        ),
        input_id="TKT-10050",
        acceptance_criteria=[
            "Urgency must be P1.",
            "The issue classification must reflect the 403 Forbidden "
            "and insufficient_scope error.",
            "Reasoning must use the fact that the error affects all users "
            "in the organisation.",
            "The response must not claim that the issue is resolved.",
            "The recommended team must be one of the configured responder teams.",
        ],
    ),
    EvaluationCase(
        case_id="T1-03",
        task="task1",
        description="Clear billing-question classification case.",
        input_id="TKT-10180",
        acceptance_criteria=[
            "The issue classification must identify the invoice/billing question.",
            "Reasoning must be grounded in the ticket's billing-related content.",
            "The response must not invent billing policies, prices, or capabilities.",
            "The recommended team must be one of the configured responder teams.",
            "Urgency must be one of P1, P2, P3, or P4.",
        ],
    ),
    EvaluationCase(
        case_id="T1-04",
        task="task1",
        description="Webhook integration failure involving AnalyticsHub and HubSpot.",
        input_id="TKT-10398",
        acceptance_criteria=[
            "The issue must be recognized as an integration/webhook problem.",
            "Urgency must be P2.",
            "Reasoning must reference the webhook delivery failure to HubSpot.",
            "The response must not invent a confirmed root cause.",
            "The matched KB document must be grounded in the retrieved KB context.",
            "The recommended team must be one of the configured responder teams.",
        ],
    ),
    EvaluationCase(
        case_id="T1-05",
        task="task1",
        description=(
            "Adversarial case where metadata says Billing but the actual "
            "ticket describes a CloudSync webhook failure."
        ),
        input_id="TKT-10002",
        acceptance_criteria=[
            "The classification must follow the actual webhook/integration "
            "problem rather than treating Billing metadata as the actual issue.",
            "Reasoning must distinguish the supplied metadata from the "
            "customer's actual problem.",
            "The response must not invent a billing issue.",
            "The response must not invent a confirmed root cause.",
            "The recommended team must be one of the configured responder teams.",
        ],
        adversarial=True,
    ),
]


TASK_2_CASES = [
    EvaluationCase(
        case_id="T2-01",
        task="task2",
        description=(
            "Adversarial At-Risk account with conflicting P1 metadata "
            "and escalation notes plus recent DataBridge Pro evidence."
        ),
        input_id="ACC-3336",
        acceptance_criteria=[
            "The summary must identify the At Risk health status.",
            "The summary must identify the Inactive usage trend.",
            "The competing-vendor evaluation must be presented as a "
            "potential churn or renewal risk, not as confirmed churn.",
            "The DataBridge Pro performance issue must be grounded in "
            "ticket TKT-10293.",
            "Ticket-derived claims must remain grounded in the supplied "
            "ticket data.",
            "The discrepancy between account metadata showing 0 P1 "
            "tickets and escalation notes stating 3 consecutive P1 "
            "tickets must not be silently resolved when materially relevant.",
            "The response must not fabricate supporting quotes.",
            "Talking points must be grounded in the supplied account "
            "and ticket data.",
        ],
        adversarial=True,
    ),

    EvaluationCase(
        case_id="T2-02",
        task="task2",
        description=(
            "Churning account with declining usage and multiple "
            "escalation signals but no supplied recent-ticket evidence."
        ),
        input_id="ACC-2944",
        acceptance_criteria=[
            "The summary must identify the Churning health status.",
            "The summary must identify the Declining usage trend.",
            "The competing-vendor evaluation must be presented as a "
            "risk, not as confirmed churn.",
            "The champion-departure signal must be treated as account "
            "metadata.",
            "The customer-frustration signal must be treated as account "
            "metadata.",
            "The procurement-related escalation signal must be treated "
            "as account metadata.",
            "The response must not invent recent tickets or "
            "ticket-derived evidence.",
            "The response must not fabricate supporting quotes.",
            "Talking points must remain grounded in the supplied "
            "account metadata.",
        ],
    ),

    EvaluationCase(
        case_id="T2-03",
        task="task2",
        description=(
            "At-Risk account with declining usage and multiple "
            "escalation signals but no supplied recent-ticket evidence."
        ),
        input_id="ACC-8113",
        acceptance_criteria=[
            "The summary must identify the At Risk health status.",
            "The summary must identify the Declining usage trend.",
            "The competing-vendor evaluation must be presented as a "
            "potential churn or renewal risk, not as confirmed churn.",
            "The pricing-review signal must be treated as account "
            "metadata.",
            "The negative-sentiment signal must be treated as account "
            "metadata.",
            "The response must not invent recent tickets or "
            "ticket-derived evidence.",
            "The response must not fabricate supporting quotes.",
            "Talking points must remain grounded in the supplied "
            "account metadata.",
        ],
    ),

    EvaluationCase(
        case_id="T2-04",
        task="task2",
        description=(
            "At-Risk account where the available ticket is outside "
            "the last-90-days evidence window."
        ),
        input_id="ACC-1785",
        acceptance_criteria=[
            "The summary must identify the At Risk health status.",
            "The summary must identify the Stable usage trend.",
            "The pricing-review signal must be treated as account "
            "metadata.",
            "The negative-sentiment signal must be treated as account "
            "metadata.",
            "The April 5, 2026 ticket TKT-10112 must not be presented "
            "as recent 90-day ticket evidence.",
            "The brief must not claim that the account currently has "
            "open tickets when account metadata shows 0 open tickets.",
            "The response must not fabricate supporting quotes.",
        ],
    ),

    EvaluationCase(
        case_id="T2-05",
        task="task2",
        description=(
            "Healthy baseline account with increasing usage and no "
            "escalation notes."
        ),
        input_id="ACC-3033",
        acceptance_criteria=[
            "The summary must identify the Healthy health status.",
            "The summary must identify the Increasing usage trend.",
            "The response must not invent escalation notes or "
            "customer sentiment.",
            "The response must not assert a churn risk without "
            "supporting evidence.",
            "The response must not invent ticket-derived evidence "
            "when no recent ticket evidence is supplied.",
            "The response must not fabricate supporting quotes.",
            "The number of open tickets must not be converted into "
            "unsupported dissatisfaction or churn claims.",
            "Talking points must remain grounded in the supplied "
            "account metadata.",
        ],
    ),
]
