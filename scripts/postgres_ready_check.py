# ============================================================================
# 💚 Core4.AI — PostgreSQL Readiness Script
# Run manually when preparing migration
# ============================================================================
import os

from config.database_config import get_database_url
from config.postgres_check import check_postgres_connection


if __name__ == "__main__":
    os.environ["DB_TYPE"] = "postgres"

    db_url = get_database_url()

    print("Checking PostgreSQL connection...")
    print("DB URL:", db_url)

    if check_postgres_connection(db_url):
        print("✅ PostgreSQL is reachable and ready.")
    else:
        print("❌ PostgreSQL connection failed.")
