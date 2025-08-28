import os
import asyncio
import asyncpg
from typing import Optional

# Global connection pool
_pool: Optional[asyncpg.Pool] = None

async def init_db() -> bool:
    """Initialize database connection pool and create tables."""
    global _pool
    
    try:
        # Get database URL from environment
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("❌ DATABASE_URL environment variable not found")
            return False
        
        # Create connection pool
        _pool = await asyncpg.create_pool(
            database_url,
            min_size=2,
            max_size=10,
            command_timeout=60
        )
        
        # Test connection and create tables
        async with _pool.acquire() as conn:
            # Create fdt_questions table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS fdt_questions (
                    question_id SERIAL PRIMARY KEY,
                    question_text TEXT NOT NULL,
                    used_at TIMESTAMP NULL
                )
            """)
            
            print("✅ Database initialized successfully")
            return True
            
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

async def get_pool() -> asyncpg.Pool:
    """Get the database connection pool."""
    global _pool
    
    if _pool is None:
        success = await init_db()
        if not success:
            raise RuntimeError("Failed to initialize database connection pool")
    
    return _pool

async def close_pool():
    """Close the database connection pool."""
    global _pool
    
    if _pool:
        await _pool.close()
        _pool = None
        print("✅ Database connection pool closed")
