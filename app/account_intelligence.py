from datetime import datetime, timedelta, timezone
from typing import List, Optional

from app.llm import GeminiClient
from app.prompts.account_evidence_prompt import (
    build_account_evidence_prompt,
)
from app.prompts.account_summary_prompt import (
    build_account_summary_prompt,
)
from app.models import (
    Account,
    AccountEvidenceResponse,
    AccountSummary,
    Ticket,
)


class AccountContext:
    """Factual account and recent-ticket context for TAM intelligence."""

    def __init__(
        self,
        account: Account,
        tickets: List[Ticket],
        reference_date: datetime,
    ):
        self.account = account
        self.tickets = tickets
        self.reference_date = reference_date

    @property
    def window_start(self) -> datetime:
        """Return the start of the 90-day ticket window."""

        return self.reference_date - timedelta(days=90)

    @property
    def ticket_count_90d(self) -> int:
        """Return the number of tickets in the 90-day window."""

        return len(self.tickets)

    @property
    def p1_ticket_count_90d(self) -> int:
        """Return the number of P1 tickets in the 90-day window."""

        return sum(
            1
            for ticket in self.tickets
            if ticket.urgency == "P1"
        )

    @property
    def active_seat_utilization(self) -> float:
        """Return active seats as a percentage of licensed seats."""

        if self.account.seats_licensed == 0:
            return 0.0

        return (
            self.account.seats_active
            / self.account.seats_licensed
        ) * 100


class AccountContextBuilder:
    """
    Builds deterministic factual context from account and ticket data.
    """

    def __init__(
        self,
        accounts: List[Account],
        tickets: List[Ticket],
        reference_date: Optional[datetime] = None,
    ):
        self.accounts = accounts
        self.tickets = tickets

        self.reference_date = (
            reference_date
            if reference_date is not None
            else self._derive_reference_date()
        )

    def _derive_reference_date(self) -> datetime:
        """
        Derive a deterministic dataset snapshot date.

        The latest ticket creation timestamp is used instead of the
        current system time so that the same dataset produces the
        same 90-day window.
        """

        if not self.tickets:
            raise ValueError(
                "Cannot derive account intelligence reference date "
                "without ticket data."
            )

        latest_ticket = max(
            self.tickets,
            key=lambda ticket: self._parse_timestamp(
                ticket.created_at
            ),
        )

        return self._parse_timestamp(latest_ticket.created_at)

    @staticmethod
    def _parse_timestamp(timestamp: str) -> datetime:
        """Parse an ISO-8601 ticket timestamp."""

        parsed = datetime.fromisoformat(
            timestamp.replace("Z", "+00:00")
        )

        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)

        return parsed

    def build(
        self,
        account_id: str,
    ) -> Optional[AccountContext]:
        """
        Build context for an account.

        Returns None when the account does not exist.
        """

        account = next(
            (
                account
                for account in self.accounts
                if account.account_id == account_id
            ),
            None,
        )

        if account is None:
            return None

        window_start = (
            self.reference_date - timedelta(days=90)
        )

        related_tickets = []

        for ticket in self.tickets:
            if ticket.account_id != account_id:
                continue

            created_at = self._parse_timestamp(
                ticket.created_at
            )

            if window_start <= created_at <= self.reference_date:
                related_tickets.append(ticket)

        # Keep ticket ordering deterministic.
        related_tickets.sort(
            key=lambda ticket: (
                self._parse_timestamp(ticket.created_at),
                ticket.ticket_id,
            ),
            reverse=True,
        )

        return AccountContext(
            account=account,
            tickets=related_tickets,
            reference_date=self.reference_date,
        )


def validate_account_evidence(
    evidence_response: AccountEvidenceResponse,
    tickets: List[Ticket],
) -> None:
    """
    Validate that ticket-derived evidence contains exact quotes
    from the referenced ticket.
    """

    ticket_lookup = {
        ticket.ticket_id: ticket
        for ticket in tickets
    }

    for evidence in evidence_response.evidence:
        if evidence.source == "ticket":
            if not evidence.ticket_id:
                raise ValueError(
                    "Ticket-derived evidence must contain a ticket_id."
                )

            ticket = ticket_lookup.get(evidence.ticket_id)

            if ticket is None:
                raise ValueError(
                    "Evidence references an unknown ticket: "
                    f"{evidence.ticket_id}"
                )

            if not evidence.supporting_quote:
                raise ValueError(
                    "Ticket-derived evidence must contain "
                    "a supporting quote."
                )

            if (
                evidence.supporting_quote not in ticket.subject
                and evidence.supporting_quote not in ticket.body
            ):
                raise ValueError(
                    "Ticket supporting quote was not found in "
                    f"{evidence.ticket_id}: "
                    f"{evidence.supporting_quote}"
                )

        elif evidence.source == "account_metadata":
            if evidence.ticket_id is not None:
                raise ValueError(
                    "Account-metadata evidence must not contain "
                    "a ticket_id."
                )

            if evidence.supporting_quote:
                raise ValueError(
                    "Account-metadata evidence must not contain "
                    "a ticket supporting quote."
                )

        else:
            raise ValueError(
                f"Unsupported evidence source: {evidence.source}"
            )


class AccountIntelligenceService:
    """
    Orchestrates account-context construction, evidence extraction,
    evidence validation, and final account-summary generation.
    """

    def __init__(
        self,
        context_builder: AccountContextBuilder,
        llm_client: GeminiClient,
    ):
        self.context_builder = context_builder
        self.llm_client = llm_client

    def analyze(
        self,
        account_id: str,
    ) -> AccountSummary:
        """
        Generate a TAM-facing account intelligence summary.
        """

        context = self.context_builder.build(account_id)

        if context is None:
            raise ValueError(
                f"Account not found: {account_id}"
            )

        # Stage 1: extract structured evidence.
        evidence_prompt = build_account_evidence_prompt(
            context.account,
            context.tickets,
        )

        evidence_response: AccountEvidenceResponse = (
            self.llm_client.generate_account_evidence(
                evidence_prompt
            )
        )

        # Validate ticket-derived evidence before using it
        # for the final synthesis.
        validate_account_evidence(
            evidence_response,
            context.tickets,
        )

        # Stage 2: synthesize the final TAM-facing summary.
        summary_prompt = build_account_summary_prompt(
            context.account,
            context.tickets,
            evidence_response.evidence,
        )

        summary = self.llm_client.generate_account_summary(
            summary_prompt
        )

        if not summary.risks:
            retry_prompt = (
                summary_prompt
                + """

        IMPORTANT CORRECTION:

        The previous response contained an empty "risks" list.

        Review the supplied account metadata and validated evidence again.
        The "risks" list must contain at least one material account risk when
        the supplied data contains a meaningful issue, escalation signal,
        support issue, usage concern, renewal concern, or other account-health
        signal.

        For example, a non-zero open-ticket count may be included as a risk
        when it is materially relevant to the account context.

        Do not invent a risk merely to satisfy this requirement.
        Every risk must still be grounded in the supplied account metadata or
        validated ticket evidence.

        Return the complete corrected JSON response only.
        """
            )

            summary = self.llm_client.generate_account_summary(
                retry_prompt
            )

        if not summary.risks:
            raise ValueError(
                "Gemini returned an account summary without any risks "
                "after retry."
            )

        return summary