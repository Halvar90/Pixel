import asyncpg
import asyncio
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def get_db_connection():
    """Erstellt eine Datenbankverbindung mit Railway-optimierter Konfiguration."""
    # Railway provides DATABASE_URL, fallback to individual variables for local development
    database_url = os.getenv('DATABASE_URL')
    
    if database_url:
        # Railway production environment
        logger.info("Connecting to database using DATABASE_URL")
        return await asyncpg.connect(database_url)
    else:
        # Local development environment
        logger.info("Connecting to database using individual environment variables")
        return await asyncpg.connect(
            user=os.getenv('POSTGRES_USER', 'postgres'),
            password=os.getenv('POSTGRES_PASSWORD', ''),
            database=os.getenv('POSTGRES_DB', 'pixel_bot_db'),
            host=os.getenv('POSTGRES_HOST', 'localhost'),
            port=os.getenv('POSTGRES_PORT', '5432')
        )

async def init_db():
    """Initialisiert die Datenbankverbindung und erstellt die Tabellen, falls sie nicht existieren."""
    max_retries = 5
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Database initialization attempt {attempt + 1}/{max_retries}")
            conn = await get_db_connection()

            # Tabelle für Spieler (globale Daten)
            await conn.execute('''
            CREATE TABLE IF NOT EXISTS players (
                user_id BIGINT PRIMARY KEY,
                pixel_balance BIGINT DEFAULT 0,
                global_upgrades JSONB DEFAULT '{}'::jsonb
            );
            ''')

            # Tabelle für die verfügbaren Welten
            await conn.execute('''
            CREATE TABLE IF NOT EXISTS worlds (
                world_id SERIAL PRIMARY KEY,
                world_name VARCHAR(255) UNIQUE NOT NULL,
                description TEXT
            );
            ''')
            
            # Tabelle, die den Fortschritt eines Spielers in einer bestimmten Welt speichert
            await conn.execute('''
            CREATE TABLE IF NOT EXISTS player_world_progress (
                progress_id SERIAL PRIMARY KEY,
                user_id BIGINT REFERENCES players(user_id) ON DELETE CASCADE,
                world_id INT REFERENCES worlds(world_id) ON DELETE CASCADE,
                is_active BOOLEAN DEFAULT false,
                world_specific_data JSONB DEFAULT '{}'::jsonb,
                UNIQUE(user_id, world_id)
            );
            ''')

            # Tabelle für alle Kreaturen, die Spieler besitzen
            await conn.execute('''
            CREATE TABLE IF NOT EXISTS creatures (
                creature_id SERIAL PRIMARY KEY,
                owner_id BIGINT REFERENCES players(user_id) ON DELETE CASCADE,
                world_id INT REFERENCES worlds(world_id) ON DELETE CASCADE,
                creature_type VARCHAR(255),
                creature_name VARCHAR(255),
                friendship_level INT DEFAULT 0
            );
            ''')
            
            logger.info("Database initialized successfully and tables created/verified.")
            await conn.close()
            return True

        except Exception as e:
            logger.error(f"Database initialization attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                logger.error("Max retries reached. Database initialization failed.")
                return False

async def get_db_pool():
    """Erstellt einen Connection Pool für bessere Performance in Production."""
    database_url = os.getenv('DATABASE_URL')
    
    if database_url:
        return await asyncpg.create_pool(
            database_url,
            min_size=1,
            max_size=10,
            command_timeout=60
        )
    else:
        return await asyncpg.create_pool(
            user=os.getenv('POSTGRES_USER', 'postgres'),
            password=os.getenv('POSTGRES_PASSWORD', ''),
            database=os.getenv('POSTGRES_DB', 'pixel_bot_db'),
            host=os.getenv('POSTGRES_HOST', 'localhost'),
            port=os.getenv('POSTGRES_PORT', '5432'),
            min_size=1,
            max_size=10,
            command_timeout=60
        )
