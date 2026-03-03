"""
Async database session and engine setup for PostgreSQL.
"""
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from core.config import settings


def _asyncpg_url_for_neon(url: str) -> tuple[str, dict]:
    """
    asyncpg does not accept sslmode/channel_binding as connect() kwargs.
    Strip them from the URL and enable SSL via connect_args.
    """
    parsed = urlparse(url)
    query = parse_qs(parsed.query, keep_blank_values=True)
    # Remove params that asyncpg doesn't accept as kwargs
    query.pop("sslmode", None)
    query.pop("channel_binding", None)
    new_query = urlencode(query, doseq=True)
    clean_url = urlunparse(parsed._replace(query=new_query))
    # Neon requires SSL; asyncpg uses ssl=True
    use_ssl = "neon.tech" in url or "sslmode=require" in url
    connect_args = {"ssl": True} if use_ssl else {}
    return clean_url, connect_args


_db_url, _connect_args = _asyncpg_url_for_neon(settings.DATABASE_URL)

# Create async engine (Neon-safe: no sslmode in URL, SSL via connect_args)
engine = create_async_engine(
    _db_url,
    echo=settings.DEBUG,
    connect_args=_connect_args,
)

# Session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    pass


async def get_db() -> AsyncSession:
    """Dependency that yields an async database session."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
