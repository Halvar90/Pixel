import asyncpg
import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class Database:
    """Datenbank-Manager für PostgreSQL."""
    
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
        self._internal_url: Optional[str] = None
        self._external_url: Optional[str] = None
    
    async def connect(self):
        """Stellt Verbindung zur Datenbank her."""
        try:
            # Railway hat interne und externe URLs
            self._internal_url = os.getenv('DATABASE_PRIVATE_URL')
            self._external_url = os.getenv('DATABASE_URL')
            
            # Versuche zuerst interne URL für bessere Performance
            database_url = self._internal_url or self._external_url
            
            if not database_url:
                raise ValueError("Keine Datenbank-URL gefunden")
            
            self.pool = await asyncpg.create_pool(
                database_url,
                min_size=1,
                max_size=10,
                command_timeout=60
            )
            
            logger.info("✅ Datenbankverbindung erfolgreich hergestellt")
            
        except Exception as e:
            logger.error(f"❌ Fehler bei Datenbankverbindung: {e}")
            raise
    
    async def disconnect(self):
        """Schließt die Datenbankverbindung."""
        if self.pool:
            await self.pool.close()
            logger.info("🔌 Datenbankverbindung geschlossen")
    
    async def execute_schema(self):
        """Führt das Schema aus data/schema.sql aus."""
        try:
            schema_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'schema.sql')
            
            if os.path.exists(schema_path):
                with open(schema_path, 'r', encoding='utf-8') as f:
                    schema_sql = f.read()
                
                async with self.pool.acquire() as conn:
                    await conn.execute(schema_sql)
                
                logger.info("✅ Datenbankschema erfolgreich ausgeführt")
            else:
                logger.warning("⚠️ schema.sql nicht gefunden")
                
        except Exception as e:
            logger.error(f"❌ Fehler beim Ausführen des Schemas: {e}")
            raise

# Globale Datenbankinstanz
db = Database()
