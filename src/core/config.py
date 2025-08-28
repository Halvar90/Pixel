import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class Config:
    """Konfiguration für den Bot."""
    
    def __init__(self):
        # Discord Bot Settings
        self.bot_token: str = os.getenv('BOT_TOKEN', '')
        self.main_guild_id: Optional[int] = None
        
        # Database Settings
        self.database_url: str = os.getenv('DATABASE_URL', '')
        self.database_private_url: str = os.getenv('DATABASE_PRIVATE_URL', '')
        
        # Redis Settings
        self.redis_url: str = os.getenv('REDIS_URL', '')
        self.redis_private_url: str = os.getenv('REDIS_PRIVATE_URL', '')
        
        # Environment
        self.environment: str = os.getenv('ENVIRONMENT', 'production')
        self.debug: bool = os.getenv('DEBUG', 'false').lower() == 'true'
        
        # Parse MAIN_GUILD_ID
        guild_id_str = os.getenv('MAIN_GUILD_ID')
        if guild_id_str:
            try:
                self.main_guild_id = int(guild_id_str)
            except ValueError:
                logger.error(f"❌ Ungültige MAIN_GUILD_ID: {guild_id_str}")
    
    def validate(self) -> bool:
        """Validiert die Konfiguration."""
        errors = []
        
        if not self.bot_token:
            errors.append("BOT_TOKEN fehlt")
        
        if not (self.database_url or self.database_private_url):
            errors.append("DATABASE_URL fehlt")
        
        if not (self.redis_url or self.redis_private_url):
            errors.append("REDIS_URL fehlt")
        
        if errors:
            for error in errors:
                logger.error(f"❌ Konfigurationsfehler: {error}")
            return False
        
        logger.info("✅ Konfiguration validiert")
        return True
    
    @property
    def is_development(self) -> bool:
        """Prüft ob im Development-Modus."""
        return self.environment == 'development'
    
    @property
    def is_production(self) -> bool:
        """Prüft ob im Production-Modus."""
        return self.environment == 'production'

# Globale Konfiguration
config = Config()
