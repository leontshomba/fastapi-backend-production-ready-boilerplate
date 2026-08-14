import logging
import sys
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.config.settings import settings

# =====================================================================
# 1. LOCAL DEVELOPMENT OBSERVABILITY & LOGGING
# =====================================================================
# In development, configure Python logging to intercept SQLAlchemy SQL engine 
# logs. This prints nicely formatted SQL statements and execution parameters.

if settings.ENVIRONMENT == "development" or settings.DEBUG:
    logging.basicConfig(
        stream=sys.stdout,
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Log generated SQL queries and parameters
    logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
else:
    # Production logging: turn off verbose SQL echoing to prevent CPU overhead and PII logging
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

# =====================================================================
# 2. PRODUCTION-READY ASYNC ENGINE
# =====================================================================
engine = create_async_engine(
    url=settings.DATABASE_URL,
    echo=False,      # Controlled via logging above for superior output formatting

    # --- Production Pool Resilience Settings ---
    pool_pre_ping=True,    # CRITICAL: Tests connection health before query execution.
    pool_size=10,
    max_overflow=20,
    pool_recycle=1800,     # Recycles connections older than 30 mins to prevent stale sockets
    pool_timeout=30,       # Seconds to wait for a pool connection before throwing a timeout error
)

# =====================================================================
# 3. ASYNC SESSION FACTORY
# =====================================================================
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,     # MANDATORY FOR ASYNC: Prevents implicit sync re-queries 
                               # when reading object attributes after session.commit()
    autoflush=False,           # Disables auto-flushing pending writes before every SELECT
)

# =====================================================================
# 4. DEPENDENCY INJECTION FOR FASTAPI ROUTES
# =====================================================================
async def get_db() -> AsyncGenerator [AsyncSession, None]:
    async with AsyncSessionLocal as session:
        try:
            yield session
        except:
            await session.rollback()
            raise
        finally:
            await session.close()