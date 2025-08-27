import asyncpg
import asyncio
import os
from lifecycle import (
    log_database_action, log_connection, log_error, log_success, 
    log_warning, log_system_event
)

async def get_db_connection():
    """Erstellt eine Datenbankverbindung mit Railway-optimierter Konfiguration."""
    # Railway provides DATABASE_URL, fallback to individual variables for local development
    database_url = os.getenv('DATABASE_URL')
    
    if database_url:
        # Railway production environment
        log_connection("PostgreSQL", "Using DATABASE_URL", "Railway production mode")
        return await asyncpg.connect(database_url)
    else:
        # Local development environment
        log_connection("PostgreSQL", "Using individual env variables", "Local development mode")
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
    
    log_database_action("Starting database initialization", "ALL", f"Max retries: {max_retries}")
    
    for attempt in range(max_retries):
        try:
            log_database_action(f"Connection attempt {attempt + 1}/{max_retries}", "CONNECTION")
            conn = await get_db_connection()
            log_connection("PostgreSQL", "Connected successfully")

            # Tabelle für Spieler (globale Daten)
            log_database_action("Creating table", "players")
            await conn.execute('''
            CREATE TABLE IF NOT EXISTS players (
                user_id BIGINT PRIMARY KEY,
                pixel_balance BIGINT DEFAULT 0,
                global_upgrades JSONB DEFAULT '{}'::jsonb
            );
            ''')

            # Tabelle für die verfügbaren Welten
            log_database_action("Creating table", "worlds")
            await conn.execute('''
            CREATE TABLE IF NOT EXISTS worlds (
                world_id SERIAL PRIMARY KEY,
                world_name VARCHAR(255) UNIQUE NOT NULL,
                description TEXT
            );
            ''')
            
            # Tabelle, die den Fortschritt eines Spielers in einer bestimmten Welt speichert
            log_database_action("Creating table", "player_world_progress")
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
            log_database_action("Creating table", "creatures")
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
            
            log_success("Database initialization completed", "All tables created/verified")
            await conn.close()
            log_connection("PostgreSQL", "Connection closed")
            return True

        except Exception as e:
            log_error(f"Database initialization attempt {attempt + 1} failed", str(e))
            if attempt < max_retries - 1:
                log_warning(f"Retrying in {retry_delay} seconds", f"Attempt {attempt + 2}/{max_retries}")
                await asyncio.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                log_error("Database initialization failed permanently", f"All {max_retries} attempts exhausted")
                return False

async def get_db_pool():
    """Erstellt einen Connection Pool für bessere Performance in Production."""
    database_url = os.getenv('DATABASE_URL')
    
    log_database_action("Creating connection pool", "CONNECTION_POOL")
    
    try:
        if database_url:
            pool = await asyncpg.create_pool(
                database_url,
                min_size=1,
                max_size=10,
                command_timeout=60
            )
        else:
            pool = await asyncpg.create_pool(
                user=os.getenv('POSTGRES_USER', 'postgres'),
                password=os.getenv('POSTGRES_PASSWORD', ''),
                database=os.getenv('POSTGRES_DB', 'pixel_bot_db'),
                host=os.getenv('POSTGRES_HOST', 'localhost'),
                port=os.getenv('POSTGRES_PORT', '5432'),
                min_size=1,
                max_size=10,
                command_timeout=60
            )
        
        log_success("Connection pool created", "Min: 1, Max: 10 connections")
        return pool
        
    except Exception as e:
        log_error("Failed to create connection pool", str(e))
        return None
