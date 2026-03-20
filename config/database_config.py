# ============================================================================
# 💚 Core4.AI — Database Configuration Layer
# Purpose:
# - Prepare PostgreSQL support
# - Do NOT override current SQLite behavior
# ============================================================================
import os


def get_database_url():
    """
    Returns DB URL based on environment.
    Default = SQLite (current behavior).
    """

    db_type = os.getenv("DB_TYPE", "sqlite")

    if db_type == "postgres":
        return os.getenv(
            "POSTGRES_URL",
            "postgresql://user:password@localhost:5432/core4"
        )

    # Default (safe)
    return "sqlite:///./core4.db"
