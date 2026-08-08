from datetime import datetime, timezone

from app.account_intelligence import AccountContextBuilder
from app.models import Account, PrimaryContact, Ticket


def create_test_account() -> Account:
    return Account(
        account_id="ACC-TEST",
        company="Test Company",
        tam="Test TAM",
        plan_tier="Business",
        arr_usd=500000,
        seats_licensed=1000,
        seats_active=750,
        products=["CloudSync"],
        health_status="At Risk",
        usage_trend="Inactive",
        open_tickets=3,
        p1_tickets_last_30d=1,
        customer_since="2025-01-01",
        renewal_date="2026-12-31",
        last_qbr_date="2026-06-01",
        primary_contact=PrimaryContact(
            name="Test Contact",
            title="CTO",
        ),
        escalation_notes=[
            "Decision maker considering competing vendor evaluation"
        ],
        nps_score=4,
        last_login_days_ago=30,
        integrations_active=["Snowflake"],
        region="US-East",
        industry="Technology",
    )


def create_test_ticket(
    ticket_id: str,
    account_id: str,
    created_at: str,
    urgency: str,
) -> Ticket:
    return Ticket(
        ticket_id=ticket_id,
        account_id=account_id,
        company="Test Company",
        subject="Test ticket",
        body="Test ticket body.",
        product="CloudSync",
        product_area="Integrations",
        category="Integration",
        urgency=urgency,
        status="Open",
        plan_tier="Business",
        assigned_agent="Test Agent",
        created_at=created_at,
        updated_at=created_at,
        tags=[],
        channel="portal",
        satisfaction_score=None,
    )


def test_account_context_builder():
    account = create_test_account()

    reference_date = datetime(
        2026,
        8,
        1,
        tzinfo=timezone.utc,
    )

    tickets = [
        # Inside 90-day window.
        create_test_ticket(
            "TKT-1",
            "ACC-TEST",
            "2026-07-15T00:00:00Z",
            "P1",
        ),
        create_test_ticket(
            "TKT-2",
            "ACC-TEST",
            "2026-06-01T00:00:00Z",
            "P2",
        ),
        # Exactly at the beginning of the 90-day window.
        create_test_ticket(
            "TKT-3",
            "ACC-TEST",
            "2026-05-03T00:00:00Z",
            "P3",
        ),
        # Outside the 90-day window.
        create_test_ticket(
            "TKT-4",
            "ACC-TEST",
            "2026-05-02T00:00:00Z",
            "P1",
        ),
        # Different account; must not be included.
        create_test_ticket(
            "TKT-5",
            "ACC-OTHER",
            "2026-07-20T00:00:00Z",
            "P1",
        ),
    ]

    builder = AccountContextBuilder(
        accounts=[account],
        tickets=tickets,
        reference_date=reference_date,
    )

    context = builder.build("ACC-TEST")

    assert context is not None
    assert context.account.account_id == "ACC-TEST"

    # Three tickets are inside the 90-day window.
    assert context.ticket_count_90d == 3

    # Only one of those tickets is P1.
    assert context.p1_ticket_count_90d == 1

    # 750 active seats out of 1000 licensed seats.
    assert context.active_seat_utilization == 75.0

    # Newest ticket should appear first.
    assert context.tickets[0].ticket_id == "TKT-1"

    # Boundary ticket is included.
    assert context.tickets[-1].ticket_id == "TKT-3"


def test_missing_account():
    account = create_test_account()

    reference_date = datetime(
        2026,
        8,
        1,
        tzinfo=timezone.utc,
    )

    builder = AccountContextBuilder(
        accounts=[account],
        tickets=[],
        reference_date=reference_date,
    )

    context = builder.build("ACC-DOES-NOT-EXIST")

    assert context is None


def test_account_with_no_recent_tickets():
    account = create_test_account()

    reference_date = datetime(
        2026,
        8,
        1,
        tzinfo=timezone.utc,
    )

    old_ticket = create_test_ticket(
        "TKT-OLD",
        "ACC-TEST",
        "2026-01-01T00:00:00Z",
        "P1",
    )

    builder = AccountContextBuilder(
        accounts=[account],
        tickets=[old_ticket],
        reference_date=reference_date,
    )

    context = builder.build("ACC-TEST")

    assert context is not None
    assert context.ticket_count_90d == 0
    assert context.p1_ticket_count_90d == 0


if __name__ == "__main__":
    test_account_context_builder()
    test_missing_account()
    test_account_with_no_recent_tickets()

    print("Account intelligence context tests passed.")