"""
Database configuration and session management.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings

def clean_database_url(url: str) -> str:
    """Clean and format database URL"""
    if not url:
        return url
    
    cleaned_url = url.strip()
    
    # Remove any trailing whitespace or newlines
    cleaned_url = cleaned_url.rstrip()
    
    return cleaned_url

def get_supabase_database_url() -> str:
    """Get Supabase database URL optimized for session mode"""
    if settings.DATABASE_URL and settings.DATABASE_URL.strip():
        cleaned_url = clean_database_url(settings.DATABASE_URL)
        
        if cleaned_url.startswith("postgresql://"):
            # Convert to asyncpg format
            if ":6543" in cleaned_url:
                print("🔄 Converting from transaction mode (6543) to session mode (5432)")
                cleaned_url = cleaned_url.replace(":6543", ":5432")
            
            # Remove any pgbouncer=true parameters for session mode
            if "pgbouncer=true" in cleaned_url:
                print("🔄 Removing pgbouncer=true parameter for session mode")
                cleaned_url = cleaned_url.replace("?pgbouncer=true", "").replace("&pgbouncer=true", "")
            
            return cleaned_url.replace("postgresql://", "postgresql+asyncpg://")
        elif cleaned_url.startswith("sqlite://"):
            return cleaned_url.replace("sqlite://", "sqlite+aiosqlite://")
        else:
            return cleaned_url
    
    # Priority 3: Fallback to SQLite for development
    print("⚠️  No database URL found, using SQLite fallback")
    return "sqlite+aiosqlite:///./slate.db"

def get_database_url_with_fallback():
    """Get database URL with proper asyncpg support"""
    # Always try to use asyncpg first
    try:
        import asyncpg
        print("✅ asyncpg is available, using asyncpg driver")
        return get_supabase_database_url()
    except ImportError:
        print("❌ asyncpg not available - this should not happen")
        # Only fallback to psycopg2 if absolutely necessary
        try:
            import psycopg2
            print("⚠️  Falling back to psycopg2")
            if settings.DATABASE_URL:
                cleaned_url = clean_database_url(settings.DATABASE_URL)
                if cleaned_url.startswith("postgresql://"):
                    if ":6543" in cleaned_url:
                        cleaned_url = cleaned_url.replace(":6543", ":5432")
                    if "pgbouncer=true" in cleaned_url:
                        cleaned_url = cleaned_url.replace("?pgbouncer=true", "").replace("&pgbouncer=true", "")
                    return cleaned_url.replace("postgresql://", "postgresql+psycopg2://")
        except ImportError:
            print("❌ Neither asyncpg nor psycopg2 available")
        
        return "sqlite+aiosqlite:///./slate.db"

# Get the Supabase database URL optimized for session mode
async_database_url = get_database_url_with_fallback()
print(f"🔧 Final database URL: {async_database_url[:50]}...")

# Async engine optimized for Supabase session mode
async_engine = create_async_engine(
    async_database_url,
    echo=settings.DEBUG,
    # Optimized settings for Supabase session mode
    connect_args={
        "command_timeout": 60,
        "server_settings": {
            "jit": "off"
        }
    } if "postgresql" in async_database_url else {},
    # Connection pooling settings optimized for Supabase
    pool_size=5,  # Smaller pool for session mode
    max_overflow=10,
    pool_recycle=1800,  # Recycle connections more frequently
    pool_pre_ping=True,
    pool_timeout=30
)

# Sync engine for migrations (using direct connection)
sync_database_url = async_database_url.replace("postgresql+asyncpg://", "postgresql://").replace("sqlite+aiosqlite://", "sqlite://")
sync_engine = create_engine(
    sync_database_url,
    echo=settings.DEBUG
)

# Session factories
AsyncSessionLocal = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

SyncSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=sync_engine
)

Base = declarative_base()

# Dependency to get async database session
async def get_async_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# Dependency to get sync database session
def get_sync_db():
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close() 