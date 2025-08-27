import asyncpg
import os

async def init_db():
    """Initialisiert die Datenbankverbindung und erstellt die Tabellen, falls sie nicht existieren."""
    try:
        conn = await asyncpg.connect(
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            database=os.getenv('POSTGRES_DB'),
            host=os.getenv('POSTGRES_HOST'),
            port=os.getenv('POSTGRES_PORT')
        )

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
        
        print("Datenbank initialisiert und Tabellen erfolgreich überprüft/erstellt.")
        await conn.close()

    except Exception as e:
        print(f"Ein Fehler bei der Datenbankinitialisierung ist aufgetreten: {e}")
        # Beende das Programm, wenn die DB nicht erreichbar ist.
        exit()
