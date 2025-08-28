"""
Test-Script für das Player-System.
Dieses Script testet die grundlegenden Funktionen des Player Cogs.
"""

import asyncio
import sys
import os

# Für lokale Imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_db_connection, init_db
from lifecycle import log_success, log_error, log_database_action

async def test_player_system():
    """Testet das Player-System."""
    try:
        log_database_action("Starting player system test", "TEST")
        
        # Initialisiere die Datenbank
        await init_db()
        log_success("Database initialized successfully")
        
        # Teste Datenbankverbindung
        conn = await get_db_connection()
        
        # Teste, ob die players Tabelle existiert
        result = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'players'
            );
        """)
        
        if result:
            log_success("Players table exists")
        else:
            log_error("Players table does not exist")
            return
        
        # Teste, ob alle erwarteten Spalten existieren
        columns = await conn.fetch("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'players'
            ORDER BY ordinal_position;
        """)
        
        expected_columns = [
            'user_id', 'pixel_balance', 'total_earned', 'total_spent',
            'global_upgrades', 'achievements', 'last_daily_bonus',
            'streak_count', 'created_at', 'updated_at'
        ]
        
        found_columns = [col['column_name'] for col in columns]
        
        log_database_action("Table structure check", "players", f"Found columns: {', '.join(found_columns)}")
        
        missing_columns = [col for col in expected_columns if col not in found_columns]
        if missing_columns:
            log_error("Missing columns", f"Missing: {', '.join(missing_columns)}")
        else:
            log_success("All expected columns found")
        
        # Teste einen einfachen Spieler-Insert
        test_user_id = 123456789
        
        # Prüfe ob Testuser bereits existiert
        existing = await conn.fetchval("SELECT user_id FROM players WHERE user_id = $1", test_user_id)
        if existing:
            await conn.execute("DELETE FROM players WHERE user_id = $1", test_user_id)
            log_database_action("Cleaned up existing test user", "players")
        
        # Erstelle Testuser
        await conn.execute(
            "INSERT INTO players (user_id, pixel_balance) VALUES ($1, $2)",
            test_user_id, 100
        )
        log_success("Test player created successfully")
        
        # Teste Balance-Update
        await conn.execute(
            "UPDATE players SET pixel_balance = pixel_balance + $1 WHERE user_id = $2",
            50, test_user_id
        )
        
        # Prüfe neuen Balance
        new_balance = await conn.fetchval("SELECT pixel_balance FROM players WHERE user_id = $1", test_user_id)
        if new_balance == 150:
            log_success(f"Balance update successful: {new_balance}")
        else:
            log_error(f"Balance update failed", f"Expected 150, got {new_balance}")
        
        # Aufräumen
        await conn.execute("DELETE FROM players WHERE user_id = $1", test_user_id)
        log_database_action("Test cleanup completed", "players")
        
        await conn.close()
        log_success("Player system test completed successfully")
        
    except Exception as e:
        log_error("Player system test failed", str(e))

if __name__ == "__main__":
    print("🧪 Testing Player System...")
    asyncio.run(test_player_system())
    print("✅ Test completed!")
