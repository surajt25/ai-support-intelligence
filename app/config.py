from pathlib import Path

# Project Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"
KB_DIR = PROJECT_ROOT / "knowledge-base"

TICKETS_FILE = DATA_DIR / "tickets.json"
ACCOUNTS_FILE = DATA_DIR / "accounts.json"


# Knowledge Base
KB_EXTENSION = ".md"


# Retrieval
TOP_K_DOCUMENTS = 3


# LLM
DEFAULT_LLM_MODEL = "gemini-3.5-flash-lite"

SIMILARITY_THRESHOLD = 0.05