# src/utils/logger.py
import logging
import sys
from datetime import datetime

def setup_logging(level=logging.INFO):
    """Konfiguriert das Logging-System für den Bot."""
    
    # Format für Log-Nachrichten
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)-15s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    
    # Root Logger konfigurieren
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(console_handler)
    
    # Discord.py Logger anpassen (weniger verbose)
    discord_logger = logging.getLogger('discord')
    discord_logger.setLevel(logging.WARNING)
    
    # Asyncio Logger anpassen
    asyncio_logger = logging.getLogger('asyncio')
    asyncio_logger.setLevel(logging.WARNING)
    
    logging.info("📝 Logging-System initialisiert")

def get_logger(name: str) -> logging.Logger:
    """Erstellt einen Logger für ein spezifisches Modul."""
    return logging.getLogger(name)
