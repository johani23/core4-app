# ====================================================================
# 💚 Core4.AI – Database (PRODUCTION READY)
# ====================================================================

import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base

# =========================================================
# ENV CONFIG
# =========================================================

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./core4.db"  # fallback for local dev
)

IS_SQLITE = DATABASE_URL.startswith("sqlite")

# =========================================================
# ENGINE
# =========================================================

if IS_SQLITE:
    engine = create_engine(
        DATABASE_URL,
        connect_args={
            "check_same_thread": False,
            "timeout": 30,
        },
    )
else:
    # 🔥 PostgreSQL / Production config
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
    )

# =========================================================
# SQLITE OPTIMIZATION (ONLY FOR SQLITE)
# =========================================================

if IS_SQLITE:
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("PRAGMA synchronous=NORMAL;")
        cursor.close()

# =========================================================
# SESSION
# =========================================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()

# =========================================================
# DEPENDENCY
# =========================================================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()