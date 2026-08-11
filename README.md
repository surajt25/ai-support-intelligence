# Zycus Assignment

This repository contains my implementation for the US Delivery Internship Technical Task Round.

The project uses the synthetic support-ticket, account, and knowledge-base data provided with the assignment.

The implementation covers two workflows:

- Ticket Triage
- Account Intelligence

A Streamlit interface is also included for running the workflows interactively.

---

## Project Structure

    Zycus_Assignment/
    │
    ├── app/
    │   ├── __init__.py
    │   ├── account_intelligence.py
    │   ├── api.py
    │   ├── config.py
    │   ├── data_loader.py
    │   ├── llm.py
    │   ├── models.py
    │   ├── retrieval.py
    │   ├── triage.py
    │   └── prompts/
    │       ├── __init__.py
    │       ├── account_evidence_prompt.py
    │       ├── account_summary_prompt.py
    │       └── triage_prompt.py
    │
    ├── data/
    │   ├── accounts.json
    │   └── tickets.json
    │
    ├── knowledge-base/
    │   ├── billing/
    │   ├── onboarding/
    │   ├── products/
    │   └── troubleshooting/
    │
    ├── tests/
    │   ├── evaluate_task1.py
    │   ├── evaluate_task2.py
    │   ├── evaluation_cases.py
    │   ├── evaluation_rules.py
    │   ├── run_task1_evaluation.py
    │   ├── run_task2_evaluation.py
    │   ├── test_account_evidence_llm.py
    │   ├── test_account_evidence_prompt.py
    │   ├── test_account_intelligence.py
    │   ├── test_account_intelligence_service.py
    │   ├── test_account_summary_llm.py
    │   ├── test_account_summary_prompt.py
    │   ├── test_data_loader.py
    │   ├── test_evaluation_cases.py
    │   ├── test_llm.py
    │   ├── test_llm_integration.py
    │   ├── test_retrieval.py
    │   ├── test_triage.py
    │   └── test_triage_prompt.py
    │
    ├── ui/
    │   └── streamlit_app.py
    │
    ├── .env.example
    ├── DATA_SCHEMA.md
    ├── eval_report_task1.json
    ├── eval_report_task2.json
    ├── pytest.ini
    ├── README.md
    └── requirements.txt

---

## Task 1 — Ticket Triage

The ticket triage workflow takes a support ticket and relevant knowledge-base documents and produces a structured triage result.

The output includes:

- Product area
- Issue category
- Urgency
- Reasoning
- Matched knowledge-base document
- Recommended responder team
- Draft customer response

The workflow uses the knowledge base as retrieval context before generating the final response.

The responder team is selected from a fixed set of configured team categories rather than being generated freely by the model.

The ticket urgency supplied in the ticket data is preserved in the structured output.

---

## Task 2 — Account Intelligence

The account intelligence workflow generates a TAM-facing account summary using account metadata and recent support tickets.

The workflow is divided into separate stages:

    Account + Recent Tickets
              |
              v
       Evidence Extraction
              |
              v
       Evidence Validation
              |
              v
        Account Summary

The final account summary contains:

- Executive summary
- Risks
- Reason for each risk
- Supporting evidence
- Ticket references where applicable
- Talking points
- Account context

The account context includes tickets associated with the account from the relevant 90-day period.

When a reference date is not explicitly provided, the implementation derives it from the latest ticket creation timestamp in the dataset. This keeps the evaluation window deterministic instead of depending on the machine's current date.

### Evidence Validation

Ticket-derived evidence is checked before it is used in the final summary.

For ticket evidence, the application verifies that:

- A ticket ID is present.
- The referenced ticket exists in the account context.
- A supporting quote is present.
- The quote occurs in the original ticket subject or body.

Account metadata evidence is handled separately and cannot contain a ticket ID or ticket-specific quote.

---

## LLM Integration

Gemini is used for the structured generation steps.

The Gemini client is implemented in:

    app/llm.py

The application requests structured responses using the Pydantic models defined in:

    app/models.py

The prompts used by the workflows are kept separately under:

    app/prompts/

This keeps prompt instructions separate from the application orchestration code.

---

## Knowledge Base Retrieval

Knowledge-base documents are stored under:

    knowledge-base/

The retrieval implementation is in:

    app/retrieval.py

Relevant documents are retrieved before the ticket-triage prompt is generated.

The retrieved document content and document path are passed to the model as context so that the triage response can be grounded in the supplied documentation.

---

## Data

The assignment provides two main datasets:

    data/tickets.json
    data/accounts.json

The tickets dataset contains synthetic support tickets.

The accounts dataset contains synthetic customer account summaries.

The knowledge base contains Markdown documents covering product information, troubleshooting, billing, and onboarding.

The complete field-level schema and example records are documented separately in:

    DATA_SCHEMA.md

The implementation also handles the documented case where a ticket references an account ID that does not have a corresponding account record.

All supplied account, ticket, and knowledge-base data is synthetic and is used as provided for the assignment.

---



## Installation

Clone the repository and move into the project directory:

    git clone https://github.com/surajt25/ai-support-intelligence.git
    cd ai-support-intelligence
    
Create a virtual environment:

    python -m venv .venv

Activate it on Windows:

    .venv\Scripts\activate

Install the required packages:

    pip install -r requirements.txt

---

## Environment Setup

Create a `.env` file in the project root:

    GEMINI_API_KEY=your_gemini_api_key_here
    GEMINI_MODEL=gemini-3.5-flash-lite

Do not commit the `.env` file.

A template is provided in:

    .env.example

---

## Running the Tests

Run the automated test suite with:

    pytest -q

The automated test suite currently contains 13 tests.

A successful run should end with:

    13 passed

---

## Running the Evaluations

### Task 1

Run:

    python -m tests.run_task1_evaluation
Output:
    
    === TASK 1 EVALUATION SUMMARY ===
    Total: 5
    Passed: 5
    Failed: 0
    Average Quality Score: 1.00
    Evaluation report written to eval_report_task1.json


### Task 2

Run:

    python -m tests.run_task2_evaluation
Output:

    === TASK 2 EVALUATION SUMMARY ===
    Total: 5
    Passed: 5
    Failed: 0
    Average Quality Score: 1.00
    Evaluation report written to eval_report_task2.json

The evaluation scripts run the defined evaluation cases and print the result and quality score for each case.

The evaluation reports are written to:

    eval_report_task1.json
    eval_report_task2.json
---

## Streamlit UI

The project includes a Streamlit interface under:

    ui/streamlit_app.py

Start it from the project root with:

    python -m streamlit run ui/streamlit_app.py

The interface provides access to the two application workflows.

### Account Intelligence

The account intelligence view allows an account to be selected and analyzed.

The result displays account information together with:

- Executive summary
- Risks
- Supporting evidence
- Talking points

### Ticket Triage

The ticket triage view accepts ticket information and generates a structured triage result.

The result includes:

- Product area
- Issue category
- Urgency
- Recommended team
- Reasoning
- Knowledge-base match
- Draft response

The UI uses the existing application services rather than implementing a separate version of the business logic.

---

## Testing and Evaluation

The repository contains both automated tests and task-specific evaluation code.

The tests cover areas including:

- Data loading
- Knowledge-base retrieval
- Ticket triage
- Prompt construction
- Account context construction
- Account evidence extraction
- Account summary generation
- Evaluation cases
- LLM integration

The evaluation scripts provide a separate check of the expected Task 1 and Task 2 behaviour.

---

## Implementation Notes

A few implementation choices are intentional.

### Structured LLM Responses

The application uses structured response models instead of relying on free-form text parsing.

### Grounded Account Evidence

Ticket-derived evidence is checked against the source ticket before it is passed to the final account-summary generation step.

### Deterministic Evaluation

The account intelligence 90-day window is based on a deterministic dataset-derived reference date when no explicit reference date is supplied.

### Fixed Responder Teams

Ticket triage uses a predefined responder-team taxonomy to avoid arbitrary team names in the generated output.

### Separation of Prompts and Services

Prompt construction is kept under `app/prompts/`, while workflow orchestration remains in the application service modules.

---

## Design Note

### 1. Failure Modes

The first major failure mode is an incorrect or unsupported LLM classification. A support ticket can be ambiguous, and the model may otherwise infer a product area or issue category that is not supported by the ticket. To reduce this risk, the triage prompt explicitly separates ticket metadata from the actual issue description and provides the knowledge-base documents as retrieval context. The output is also requested through a structured Pydantic response model rather than free-form text. Automated tests check important parts of the prompt and output contract, while the evaluation harness provides regression checks across representative cases.

The second failure mode is unsupported account-health evidence. Account intelligence combines account metadata with recent tickets, so an LLM could potentially generate a risk that is not actually supported by the source data or invent a ticket quotation. The implementation addresses this with a two-stage process. The first LLM call extracts structured evidence, and the application validates every ticket-derived quote against the original ticket subject or body before the evidence is passed to the final summary generation step. Invalid ticket references or quotes cause validation to fail instead of silently entering the final summary.

The third failure mode is external LLM/API failure, including quota exhaustion, missing credentials, or an unavailable model. The Gemini client checks that the API key is configured and raises explicit errors when a structured response is missing or invalid. Evaluation execution is also separated from the application's core logic, so an API failure is reported as a failed evaluation case rather than being mistaken for a successful result.

### 2. Latency vs Quality

The main latency versus quality trade-off is in account intelligence. Instead of making one large LLM request containing all account data and asking the model to directly produce the final summary, the implementation uses two generation stages: evidence extraction followed by summary synthesis. This introduces an additional LLM call and therefore increases latency and API usage, but it provides a stronger grounding boundary between source data and the final TAM-facing output.

The additional validation step is deliberately performed in Python rather than asking the model to validate its own evidence. This adds processing but is deterministic and inexpensive compared with another model call. If latency became the hard constraint, I would consider reducing the workflow to a single generation step for less critical accounts, while retaining deterministic validation for any ticket-derived evidence. Another option would be caching retrieved knowledge-base documents and previously generated account evidence.

### 3. Data Sensitivity

The assignment data is synthetic, but the production design assumes that support tickets and account records may contain personally identifiable or commercially sensitive information. The application should therefore send only the minimum information required for the requested task to the external LLM API. For ticket triage, this means providing the ticket content and relevant knowledge-base context rather than unrelated account records. For account intelligence, only the selected account and its relevant ticket history are included.

API credentials are loaded from environment variables through `.env` and are not stored in source code. The real `.env` file is excluded through `.gitignore`, while `.env.example` contains only placeholder configuration. In a production environment, I would additionally use a managed secret store, apply access controls, define appropriate data-retention settings for the LLM provider, and consider redaction of unnecessary PII before sending content to an external model.

### 4. Scaling

With ten times the current ticket volume, the first issue would be retrieval and data-processing efficiency rather than the LLM itself. The current mock dataset is small enough for an in-memory retrieval index and straightforward filtering. At larger volumes, rebuilding or searching the entire corpus for every request would become increasingly expensive.

The retrieval layer should therefore be moved to a persistent vector or search index, with documents embedded once and incrementally updated when the knowledge base changes. Ticket and account data should also be stored behind indexed queries rather than repeatedly loading the complete JSON datasets into memory. Account intelligence could process only the selected account's recent tickets, keeping the amount of context sent to the LLM bounded.

The LLM layer would also require rate limiting, retries with backoff, request monitoring, and potentially asynchronous processing for batch account analysis. Evaluation should continue to run against a fixed test set so that changes to retrieval, prompts, models, or validation logic can be detected before deployment.

---

## Additional Features

### Streamlit UI

A Streamlit interface is included for non-technical users to interact with both workflows.

The UI supports:

- Ticket triage
- Account intelligence
- Structured display of generated results

### Prompt Versioning

The prompts include explicit version identifiers for traceability and evaluation.

For example, the ticket triage prompt defines a `PROMPT_VERSION` value that is included in the generated prompt.

This makes prompt changes easier to track when comparing evaluation results.

