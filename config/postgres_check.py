# ============================================================================
# 💚 Core4.AI — PostgreSQL Safety Check
# Purpose:
# - Verify Postgres connection BEFORE switching
# ============================================================================
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError


def check_postgres_connection(db_url: str) -> bool:
    try:
        engine = create_engine(db_url)
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return True
    except OperationalError:
        return False
