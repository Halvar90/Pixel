# src/utils/logger.py
"""
Erweiterte Logging-Konfiguration mit schönen Formatierungen
Für benutzerfreundliche und ansprechende Logs
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path

class UnicodeFormatter(logging.Formatter):
    """Schöner Unicode-Formatter mit Emojis und besserer Lesbarkeit"""
    
    # Mapping von Log-Levels zu schönen Emojis und Beschreibungen
    LEVEL_STYLES = {
        'DEBUG': {'emoji': '🔍', 'color': 'cyan', 'desc': 'Debug'},
        'INFO': {'emoji': '📝', 'color': 'green', 'desc': 'Info'},
        'WARNING': {'emoji': '⚠️', 'color': 'yellow', 'desc': 'Warnung'},
        'ERROR': {'emoji': '❌', 'color': 'red', 'desc': 'Fehler'},
        'CRITICAL': {'emoji': '💥', 'color': 'magenta', 'desc': 'Kritisch'},
    }
    
    # Spezielle Logger mit eigenen Emojis
    LOGGER_EMOJIS = {
        'discord.client': '🔌',
        'discord.gateway': '🌐',
        'discord.http': '📡',
        'src.bot': '🤖',
        'src.cogs': '⚙️',
        'src.utils': '🛠️',
        'src.systems': '🧠',
        'src.systems.migration_system': '💾',
        'src.systems.command_registration_system': '🎯',
        'alembic': '🔄',
        'asyncpg': '🐘',
        'railway': '🚂',
    }
    
    def __init__(self, use_colors=True):
        super().__init__()
        self.use_colors = use_colors
        
    def format(self, record):
        # Basis-Style für das Level
        level_style = self.LEVEL_STYLES.get(record.levelname, {
            'emoji': '📋', 'color': 'white', 'desc': record.levelname
        })
        
        # Logger-spezifisches Emoji
        logger_emoji = self.LOGGER_EMOJIS.get(record.name, '📦')
        
        # Logger-Namen verkürzen für bessere Lesbarkeit
        logger_name = self._format_logger_name(record.name)
        
        # Nachricht formatieren
        message = record.getMessage()
        
        # Special Message Formatting
        if record.levelname == 'INFO':
            message = self._enhance_info_message(message)
        elif record.levelname == 'ERROR':
            message = self._enhance_error_message(message)
        elif record.levelname == 'WARNING':
            message = self._enhance_warning_message(message)
        
        # Finale Formatierung - ohne Timestamp (Railway fügt eigene hinzu)
        formatted = (
            f"{level_style['emoji']} "
            f"{logger_emoji} "
            f"{logger_name}: "
            f"{message}"
        )
        
        return formatted
    
    def _format_logger_name(self, name):
        """Verkürzt und verschönert Logger-Namen"""
        if name == 'root':
            return 'Bot'
        elif name.startswith('src.'):
            return name.replace('src.', '').title()
        elif name.startswith('discord.'):
            return name.replace('discord.', 'Discord-').title()
        elif name == 'alembic.runtime.migration':
            return 'Migration'
        elif name.startswith('alembic'):
            return 'Alembic'
        else:
            return name.split('.')[-1].title()
    
    def _enhance_info_message(self, message):
        """Verbessert INFO-Nachrichten mit zusätzlichen Emojis"""
        if 'Setup' in message or 'setup' in message:
            return f"🔧 {message}"
        elif 'geladen' in message or 'loaded' in message:
            return f"✅ {message}"
        elif 'online' in message or 'bereit' in message:
            return f"🚀 {message}"
        elif 'synchronisiert' in message or 'synced' in message:
            return f"🔄 {message}"
        elif 'Migration' in message:
            return f"💾 {message}"
        elif 'Command' in message:
            return f"🎯 {message}"
        else:
            return message
    
    def _enhance_error_message(self, message):
        """Verbessert ERROR-Nachrichten"""
        if 'Extension' in message and 'has no' in message:
            return f"📦 Modul-Fehler: {message}"
        elif 'setup' in message:
            return f"⚙️ Setup-Fehler: {message}"
        elif 'connection' in message.lower():
            return f"🔌 Verbindungs-Fehler: {message}"
        elif 'database' in message.lower() or 'db' in message.lower():
            return f"💾 Datenbank-Fehler: {message}"
        else:
            return f"💥 {message}"
    
    def _enhance_warning_message(self, message):
        """Verbessert WARNING-Nachrichten"""
        if 'PyNaCl' in message:
            return f"🔊 Voice-Warnung: {message}"
        elif 'nicht gesetzt' in message or 'not set' in message:
            return f"⚙️ Konfigurations-Warnung: {message}"
        else:
            return f"⚠️ {message}"


class ProgressLogger:
    """Logger für Fortschritts-Anzeigen und bessere Struktur"""
    
    def __init__(self, logger):
        self.logger = logger
        
    def start_section(self, title, emoji="🔧"):
        """Startet eine neue Sektion mit schöner Formatierung"""
        border = "=" * 50
        self.logger.info(f"\n{border}")
        self.logger.info(f"{emoji} {title.upper()}")
        self.logger.info(f"{border}")
    
    def step(self, step_num, total_steps, description, emoji="📝"):
        """Zeigt einen Schritt im Fortschritt an"""
        progress = f"[{step_num}/{total_steps}]"
        self.logger.info(f"{emoji} {progress} {description}")
    
    def success(self, message, emoji="✅"):
        """Erfolgreiche Vollendung"""
        self.logger.info(f"{emoji} ERFOLGREICH: {message}")
    
    def warning(self, message, emoji="⚠️"):
        """Warnung mit spezieller Formatierung"""
        self.logger.warning(f"{emoji} ACHTUNG: {message}")
    
    def error(self, message, emoji="❌"):
        """Fehler mit spezieller Formatierung"""
        self.logger.error(f"{emoji} FEHLER: {message}")
    
    def end_section(self, success=True):
        """Beendet eine Sektion"""
        if success:
            self.logger.info("✅ SEKTION ERFOLGREICH ABGESCHLOSSEN\n")
        else:
            self.logger.error("❌ SEKTION MIT FEHLERN ABGESCHLOSSEN\n")


def setup_logging(level=logging.INFO, log_to_file=True, enhanced=True):
    """
    Konfiguriert das erweiterte Logging-System für den Bot
    
    Args:
        level: Logging-Level (default: INFO)
        log_to_file: Ob in Datei geloggt werden soll
        enhanced: Ob das erweiterte schöne Format verwendet werden soll
    """
    
    # Root Logger konfigurieren
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Alle bestehenden Handler entfernen
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    if enhanced:
        # Schöner Unicode-Formatter mit Emojis
        console_formatter = UnicodeFormatter(use_colors=True)
    else:
        # Klassischer Formatter
        console_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)-15s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File Handler (optional)
    if log_to_file:
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"bot_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)  # Datei bekommt alle Logs
        
        # Datei bekommt Unicode-Format ohne Farben
        file_formatter = UnicodeFormatter(use_colors=False)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
    
    # Discord.py Logger anpassen (weniger verbose)
    discord_logger = logging.getLogger('discord')
    discord_logger.setLevel(logging.WARNING)
    
    # Discord HTTP Logs reduzieren (sind sehr verbose)
    http_logger = logging.getLogger('discord.http')
    http_logger.setLevel(logging.ERROR)
    
    # Asyncio Logger anpassen
    asyncio_logger = logging.getLogger('asyncio')
    asyncio_logger.setLevel(logging.WARNING)
    
    # Alembic Logs anpassen
    alembic_logger = logging.getLogger('alembic')
    alembic_logger.setLevel(logging.INFO)
    
    if enhanced:
        # Schöne Willkommensnachricht
        banner_logger = logging.getLogger('banner')
        banner_logger.info("")
        banner_logger.info("🌟" + "=" * 48 + "🌟")
        banner_logger.info("🌟" + " " * 16 + "PIXEL DISCORD BOT" + " " * 16 + "🌟")
        banner_logger.info("🌟" + "=" * 48 + "🌟")
        banner_logger.info(f"🕐 Gestartet am: {datetime.now().strftime('%d.%m.%Y um %H:%M:%S')}")
        banner_logger.info(f"🐍 Python Version: {sys.version.split()[0]}")
        banner_logger.info("🌟" + "=" * 48 + "🌟")
        banner_logger.info("")
    else:
        logging.info("📝 Logging-System initialisiert")
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """Erstellt einen Logger für ein spezifisches Modul."""
    return logging.getLogger(name)


def create_progress_logger(name="progress"):
    """Erstellt einen Progress-Logger für spezielle Fortschritts-Logs"""
    logger = logging.getLogger(name)
    return ProgressLogger(logger)


# Spezielle Logger für verschiedene Bot-Bereiche
def get_bot_logger(name):
    """Gibt einen konfigurierten Logger für Bot-Komponenten zurück"""
    return logging.getLogger(f"src.{name}")


def get_system_logger(name):
    """Gibt einen konfigurierten Logger für System-Komponenten zurück"""
    return logging.getLogger(f"src.systems.{name}")


# Praktische Logging-Funktionen für häufige Anwendungsfälle
def log_startup_step(step_num, total_steps, description):
    """Loggt einen Startup-Schritt"""
    logger = logging.getLogger("startup")
    progress = f"[{step_num}/{total_steps}]"
    logger.info(f"🚀 {progress} {description}")


def log_cog_loading(cog_name, success=True, error=None):
    """Loggt das Laden eines Cogs"""
    logger = logging.getLogger("cogs")
    if success:
        logger.info(f"⚙️ Cog '{cog_name}' erfolgreich geladen")
    else:
        logger.error(f"❌ Fehler beim Laden von Cog '{cog_name}': {error}")


def log_system_status(system_name, status, details=None):
    """Loggt System-Status"""
    logger = logging.getLogger("systems")
    if status == "success":
        logger.info(f"✅ System '{system_name}' erfolgreich initialisiert")
        if details:
            logger.info(f"   📊 Details: {details}")
    elif status == "warning":
        logger.warning(f"⚠️ System '{system_name}' mit Warnungen gestartet")
        if details:
            logger.warning(f"   ⚠️ Details: {details}")
    else:
        logger.error(f"❌ System '{system_name}' fehlgeschlagen")
        if details:
            logger.error(f"   💥 Details: {details}")


def log_database_operation(operation, success=True, details=None):
    """Loggt Datenbank-Operationen"""
    logger = logging.getLogger("database")
    if success:
        logger.info(f"💾 Datenbank-Operation '{operation}' erfolgreich")
        if details:
            logger.info(f"   📊 {details}")
    else:
        logger.error(f"❌ Datenbank-Operation '{operation}' fehlgeschlagen")
        if details:
            logger.error(f"   💥 {details}")


def log_command_sync(count, sync_type="global", success=True):
    """Loggt Command-Synchronisation"""
    logger = logging.getLogger("commands")
    if success:
        logger.info(f"🎯 {count} Commands erfolgreich synchronisiert ({sync_type})")
    else:
        logger.error(f"❌ Fehler bei Command-Synchronisation ({sync_type})")


def log_bot_ready(guild_count, user_count=None):
    """Loggt Bot-Ready-Status"""
    logger = logging.getLogger("bot")
    logger.info(f"🤖 Bot ist bereit und online!")
    logger.info(f"📊 Aktiv in {guild_count} Servern")
    if user_count:
        logger.info(f"👥 Erreicht {user_count} Benutzer")
