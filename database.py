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
            
            # Create bot_settings table for channel configuration
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS bot_settings (
                    setting_key VARCHAR(50) PRIMARY KEY,
                    setting_value VARCHAR(200) NOT NULL,
                    description TEXT,
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Insert default channel settings if they don't exist
            await conn.execute("""
                INSERT INTO bot_settings (setting_key, setting_value, description) 
                VALUES 
                    ('fdt_channel_id', '1410229292230508595', 'Channel for daily questions'),
                    ('main_chat_channel_id', '1270678012341387268', 'Channel for notifications')
                ON CONFLICT (setting_key) DO NOTHING
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

async def get_channel_setting(setting_key: str) -> Optional[int]:
    """Get a channel ID from bot settings."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        result = await conn.fetchval(
            "SELECT setting_value FROM bot_settings WHERE setting_key = $1", 
            setting_key
        )
        return int(result) if result else None

async def set_channel_setting(setting_key: str, channel_id: int, description: str = None) -> bool:
    """Set a channel ID in bot settings."""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO bot_settings (setting_key, setting_value, description, updated_at) 
                VALUES ($1, $2, $3, NOW())
                ON CONFLICT (setting_key) 
                DO UPDATE SET setting_value = $2, description = COALESCE($3, bot_settings.description), updated_at = NOW()
            """, setting_key, str(channel_id), description)
            return True
    except Exception as e:
        print(f"❌ Error setting channel: {e}")
        return False

async def get_fdt_channel_id() -> Optional[int]:
    """Get the FdT channel ID."""
    return await get_channel_setting('fdt_channel_id')

async def get_main_chat_channel_id() -> Optional[int]:
    """Get the main chat channel ID."""
    return await get_channel_setting('main_chat_channel_id')
