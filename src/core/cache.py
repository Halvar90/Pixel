import redis.asyncio as redis
import os
import json
import logging
from typing import Optional, Any

logger = logging.getLogger(__name__)

class Cache:
    """Redis-Cache-Manager."""
    
    def __init__(self):
        self.redis: Optional[redis.Redis] = None
        self._internal_url: Optional[str] = None
        self._external_url: Optional[str] = None
    
    async def connect(self):
        """Stellt Verbindung zu Redis her."""
        try:
            # Railway hat interne und externe URLs
            self._internal_url = os.getenv('REDIS_PRIVATE_URL')
            self._external_url = os.getenv('REDIS_URL')
            
            # Versuche zuerst interne URL für bessere Performance
            redis_url = self._internal_url or self._external_url
            
            if not redis_url:
                raise ValueError("Keine Redis-URL gefunden")
            
            self.redis = redis.from_url(
                redis_url,
                decode_responses=True,
                socket_timeout=30,
                socket_connect_timeout=30,
                health_check_interval=30
            )
            
            # Teste die Verbindung
            await self.redis.ping()
            
            logger.info("✅ Redis-Verbindung erfolgreich hergestellt")
            
        except Exception as e:
            logger.error(f"❌ Fehler bei Redis-Verbindung: {e}")
            raise
    
    async def disconnect(self):
        """Schließt die Redis-Verbindung."""
        if self.redis:
            await self.redis.aclose()
            logger.info("🔌 Redis-Verbindung geschlossen")
    
    async def set(self, key: str, value: Any, expire: Optional[int] = None):
        """Setzt einen Wert im Cache."""
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            
            await self.redis.set(key, value, ex=expire)
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Setzen von Cache-Wert {key}: {e}")
    
    async def get(self, key: str) -> Optional[Any]:
        """Holt einen Wert aus dem Cache."""
        try:
            value = await self.redis.get(key)
            if value is None:
                return None
            
            # Versuche JSON zu parsen
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
                
        except Exception as e:
            logger.error(f"❌ Fehler beim Abrufen von Cache-Wert {key}: {e}")
            return None
    
    async def delete(self, key: str):
        """Löscht einen Wert aus dem Cache."""
        try:
            await self.redis.delete(key)
        except Exception as e:
            logger.error(f"❌ Fehler beim Löschen von Cache-Wert {key}: {e}")
    
    async def set_cooldown(self, key: str, seconds: int):
        """Setzt einen Cooldown."""
        await self.set(key, "on_cooldown", expire=seconds)
    
    async def is_on_cooldown(self, key: str) -> bool:
        """Prüft ob ein Cooldown aktiv ist."""
        value = await self.get(key)
        return value is not None
    
    async def get_cooldown_remaining(self, key: str) -> int:
        """Gibt die verbleibende Cooldown-Zeit in Sekunden zurück."""
        try:
            ttl = await self.redis.ttl(key)
            return max(0, ttl)
        except Exception:
            return 0

# Globale Cache-Instanz
cache = Cache()
