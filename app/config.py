
r"""
from pathlib import Path

# root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Data paths
DATA_DIR = PROJECT_ROOT / "data"
KB_DIR = PROJECT_ROOT / "knowledge-base"

TICKETS_FILE = DATA_DIR / "tickets.json"
ACCOUNTS_FILE = DATA_DIR / "accounts.json"

# Supported markdown extension
KB_EXTENSION = ".md"

# Retrieval defaults
TOP_K_DOCUMENTS = 3

"""






from pathlib import Path

# ==========================
# Project Paths
# ==========================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"
KB_DIR = PROJECT_ROOT / "knowledge-base"

TICKETS_FILE = DATA_DIR / "tickets.json"
ACCOUNTS_FILE = DATA_DIR / "accounts.json"

# ==========================
# Knowledge Base
# ==========================

KB_EXTENSION = ".md"

# ==========================
# Retrieval
# ==========================

TOP_K_DOCUMENTS = 3

# ==========================
# LLM Defaults
# ==========================

DEFAULT_LLM_MODEL = "gpt-5.5"
TEMPERATURE = 0