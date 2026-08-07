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