import sys
from pathlib import Path

import streamlit as st

# Make the project root importable when Streamlit runs this file.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.account_intelligence import (
    AccountContextBuilder,
    AccountIntelligenceService,
)
from app.data_loader import DataLoader
from app.llm import GeminiClient
from app.retrieval import KnowledgeBaseRetriever
from app.triage import TriageService
from app.models import Ticket


# Page configuration

st.set_page_config(
    page_title="Zycus AI Support Intelligence",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Styling
st.markdown(
    """
    <style>
        .main {
            background-color: #f7f8fa;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1400px;
        }

        .app-title {
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 0.2rem;
        }

        .app-subtitle {
            color: #6b7280;
            font-size: 1rem;
            margin-bottom: 1.5rem;
        }

        .metric-card {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 1rem 1.2rem;
            min-height: 110px;
        }

        .metric-label {
            color: #6b7280;
            font-size: 0.85rem;
            margin-bottom: 0.35rem;
        }

        .metric-value {
            font-size: 1.45rem;
            font-weight: 700;
            color: #111827;
        }

        .risk-card {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 10px;
            padding: 1rem;
            margin-bottom: 0.8rem;
        }

        .risk-title {
            font-weight: 700;
            font-size: 1rem;
            margin-bottom: 0.4rem;
        }

        .section-title {
            font-size: 1.25rem;
            font-weight: 650;
            margin-top: 1.5rem;
            margin-bottom: 0.8rem;
        }

        .info-box {
            background: white;
            color: #111827;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 1.2rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# Cached application resources
@st.cache_resource
def get_llm_client():
    return GeminiClient()


@st.cache_resource
def get_triage_service():
    loader = DataLoader()

    documents = loader.load_knowledge_base()

    retriever = KnowledgeBaseRetriever()
    retriever.build_index(documents)

    return TriageService(
        retriever=retriever,
        llm_client=get_llm_client(),
    )


@st.cache_resource
def get_account_service():
    loader = DataLoader()

    accounts = loader.load_accounts()
    tickets = loader.load_tickets()

    context_builder = AccountContextBuilder(
        accounts,
        tickets,
    )

    return AccountIntelligenceService(
        context_builder=context_builder,
        llm_client=get_llm_client(),
    )


@st.cache_data
def load_data():
    loader = DataLoader()

    return (
        loader.load_accounts(),
        loader.load_tickets(),
    )


# Header
st.markdown(
    '<div class="app-title">Zycus AI Support Intelligence</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="app-subtitle">'
    "Technical Support triage and TAM account intelligence workspace"
    "</div>",
    unsafe_allow_html=True,
)


# Sidebar
with st.sidebar:
    st.markdown("## Workspace")

    page = st.radio(
        "Select a workflow",
        [
            "Account Intelligence",
            "Ticket Triage",
        ],
    )

    st.divider()

    st.caption(
        "Powered by the project's existing "
        "Gemini, retrieval, and validation services."
    )


# ACCOUNT INTELLIGENCE
if page == "Account Intelligence":

    accounts, _ = load_data()

    st.markdown("## Account Intelligence")
    st.write(
        "Generate a concise account brief from account metadata "
        "and recent ticket history."
    )

    account_options = {
        f"{account.company} — {account.account_id}": account
        for account in accounts
    }

    selected_label = st.selectbox(
        "Account",
        list(account_options.keys()),
    )

    account = account_options[selected_label]

    # Account overview
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Health Status</div>
                <div class="metric-value">{account.health_status}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Usage Trend</div>
                <div class="metric-value">{account.usage_trend}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">ARR</div>
                <div class="metric-value">${account.arr_usd:,.0f}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Renewal Date</div>
                <div class="metric-value">{account.renewal_date}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")

    if st.button(
        "Generate Account Brief",
        type="primary",
        use_container_width=True,
    ):
        with st.spinner("Building account intelligence..."):
            try:
                service = get_account_service()

                result = service.analyze(
                    account.account_id
                )

                st.session_state["account_result"] = result

            except Exception as exc:
                st.error(
                    f"Unable to generate the account brief: {exc}"
                )

    result = st.session_state.get("account_result")

    if result is not None:

        st.markdown(
            '<div class="section-title">Executive Summary</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="info-box">{result.executive_summary}</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="section-title">Risks & Flagged Issues</div>',
            unsafe_allow_html=True,
        )

        if result.risks:

            for risk in result.risks:

                with st.container(border=True):

                    st.markdown(
                        f"### {risk.title}"
                    )

                    st.write(
                        f"**Reason:** {risk.reason}"
                    )

                    if risk.supporting_quote:
                        st.write(
                            f"**Supporting quote:** "
                            f'"{risk.supporting_quote}"'
                        )

                    if risk.source:
                        st.caption(
                            f"Source: {risk.source}"
                            + (
                                f" · Ticket: {risk.ticket_id}"
                                if risk.ticket_id
                                else ""
                            )
                        )

        else:
            st.info(
                "No material risks were identified from the supplied data."
            )

        st.markdown(
            '<div class="section-title">Talking Points</div>',
            unsafe_allow_html=True,
        )

        for point in result.talking_points:
            st.markdown(f"- {point}")


# TICKET TRIAGE
else:

    st.markdown("## Ticket Triage")
    st.write(
        "Analyze an incoming support ticket and generate "
        "structured routing and response guidance."
    )

    col1, col2 = st.columns(2)

    with col1:
        subject = st.text_input(
            "Ticket subject",
            placeholder="Example: API requests timing out",
        )

    with col2:
        company = st.text_input(
            "Company",
            placeholder="Customer company name",
        )

    body = st.text_area(
        "Ticket body",
        height=220,
        placeholder=(
            "Describe the customer's issue, symptoms, "
            "impact, and any relevant error messages..."
        ),
    )

    st.caption(
        "The submitted subject and body are analyzed using the "
        "existing triage and knowledge-base retrieval pipeline."
    )

    if st.button(
        "Analyze Ticket",
        type="primary",
        use_container_width=True,
    ):

        if not subject.strip() or not body.strip():
            st.warning(
                "Please provide both a ticket subject and ticket body."
            )

        else:

            try:
                with st.spinner("Analyzing ticket..."):

                    ticket = Ticket(
                        ticket_id="UI-TICKET",
                        account_id="UI-ACCOUNT",
                        company=company.strip() or "Unknown",
                        subject=subject.strip(),
                        body=body.strip(),
                        product="Unknown",
                        product_area="Unknown",
                        category="Unknown",
                        urgency="P4",
                        status="Open",
                        plan_tier="Unknown",
                        assigned_agent="Unassigned",
                        created_at="",
                        updated_at="",
                        tags=[],
                        channel="ui",
                        satisfaction_score=None,
                    )

                    service = get_triage_service()

                    result = service.triage(ticket)

                    st.session_state["triage_result"] = result

            except Exception as exc:
                st.error(
                    f"Unable to analyze the ticket: {exc}"
                )

    result = st.session_state.get("triage_result")

    if result is not None:

        st.markdown(
            '<div class="section-title">Triage Result</div>',
            unsafe_allow_html=True,
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">Urgency</div>
                    <div class="metric-value">{result.urgency}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col2:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">Issue Category</div>
                    <div class="metric-value">
                        {result.issue_category}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col3:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">Product Area</div>
                    <div class="metric-value">
                        {result.product_area}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown(
            '<div class="section-title">Routing</div>',
            unsafe_allow_html=True,
        )

        st.info(
            f"Recommended responder team: "
            f"**{result.recommended_team}**"
        )

        col1, col2 = st.columns(2)

        with col1:
            with st.container(border=True):
                st.markdown("### Reasoning")
                st.write(result.reasoning)

        with col2:
            with st.container(border=True):
                st.markdown("### Knowledge Base Match")
                st.write(result.matched_kb_document)

        st.markdown(
            '<div class="section-title">Draft First Response</div>',
            unsafe_allow_html=True,
        )

        with st.container(border=True):
            st.write(result.draft_response)