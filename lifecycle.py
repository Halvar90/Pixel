# Filename: lifecycle.py
# Verbesserte Logging-Funktionen für Pixel Bot nach Codex-Vorbild

import logging
import os
from collections import deque
from datetime import datetime, timezone

# Eine spezielle Liste, die nur die letzten 100 Events im Speicher hält
# 'appendleft' sorgt dafür, dass die neuesten Events immer am Anfang stehen
_recent_events = deque(maxlen=100)

def setup_logging():
    """Konfiguriert das gesamte Logging-System für eine saubere, lesbare Ausgabe."""
    # Einfaches Format ohne Timestamp - Railway zeigt bereits Timestamps
    fmt = "%(message)s"
    
    # Stellt sicher, dass Logs sofort in Railway erscheinen
    os.environ.setdefault("PYTHONUNBUFFERED", "1")
    
    # Konfiguriert den Haupt-Logger - ohne datefmt da Railway bereits Timestamps zeigt
    logging.basicConfig(level=logging.INFO, format=fmt)

    # Reduziert das "Geschwätz" von externen Bibliotheken, um die Logs sauber zu halten
    logging.getLogger("discord").setLevel(logging.WARNING)
    logging.getLogger("websockets").setLevel(logging.WARNING)
    logging.getLogger("asyncpg").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)

# Rufe die Funktion einmal beim Import auf, um das Logging zu aktivieren
setup_logging()

def log_story(emoji: str, message: str):
    """Loggt eine Nachricht mit einem vorangestellten Emoji und speichert sie für die Diagnose-API."""
    full_message = f"{emoji} {message}"
    logging.info(full_message)
    
    # Füge das Event zur Liste für die API hinzu
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    _recent_events.appendleft(f"[{timestamp}] {full_message}")

def get_recent_events(limit: int = 50) -> list:
    """Gibt eine Liste der letzten Log-Events zurück."""
    # Gibt eine Kopie der Liste zurück, um Thread-Safety zu gewährleisten
    return list(_recent_events)[:limit]

# Spezielle Logging-Funktionen für verschiedene Ereignisse
def log_user_action(action: str, user_name: str, details: str = ""):
    """Loggt Benutzeraktionen im Pixel Bot"""
    message = f"User '{user_name}' - {action}"
    if details:
        message += f" ({details})"
    log_story("👤", message)

def log_game_action(action: str, player: str, details: str = ""):
    """Loggt Spieleraktionen (Pixel-spezifisch)"""
    message = f"Player '{player}' - {action}"
    if details:
        message += f" ({details})"
    log_story("🎮", message)

def log_pixel_economy(action: str, player: str, amount: int, details: str = ""):
    """Loggt Pixel-Wirtschaft Aktionen"""
    message = f"Economy: {action} for '{player}' - {amount} pixels"
    if details:
        message += f" ({details})"
    log_story("💰", message)

def log_world_action(action: str, world: str, player: str = "", details: str = ""):
    """Loggt Welt-bezogene Aktionen"""
    message = f"World '{world}': {action}"
    if player:
        message += f" by '{player}'"
    if details:
        message += f" - {details}"
    log_story("🌍", message)

def log_creature_action(action: str, creature: str, owner: str, details: str = ""):
    """Loggt Kreatur-bezogene Aktionen"""
    message = f"Creature '{creature}' ({owner}) - {action}"
    if details:
        message += f" ({details})"
    log_story("🐾", message)

def log_database_action(action: str, table: str, details: str = ""):
    """Loggt Datenbankaktionen"""
    message = f"DB {action} in {table}"
    if details:
        message += f" - {details}"
    log_story("🗄️", message)

def log_bot_event(event: str, details: str = ""):
    """Loggt Bot-spezifische Events"""
    message = f"Bot Event: {event}"
    if details:
        message += f" - {details}"
    log_story("🤖", message)

def log_system_event(event: str, details: str = ""):
    """Loggt System-Events"""
    message = f"System: {event}"
    if details:
        message += f" - {details}"
    log_story("⚙️", message)

def log_railway_event(event: str, details: str = ""):
    """Loggt Railway-spezifische Events"""
    message = f"Railway: {event}"
    if details:
        message += f" - {details}"
    log_story("🚂", message)

def log_command_usage(command: str, user: str, guild: str = "", details: str = ""):
    """Loggt Command-Nutzung"""
    message = f"Command '{command}' used by '{user}'"
    if guild:
        message += f" in '{guild}'"
    if details:
        message += f" - {details}"
    log_story("⚡", message)

def log_error(error_type: str, details: str = "", user: str = ""):
    """Loggt Fehler mit spezieller Formatierung"""
    message = f"ERROR: {error_type}"
    if user:
        message += f" (User: {user})"
    if details:
        message += f" - {details}"
    log_story("❌", message)

def log_success(action: str, details: str = ""):
    """Loggt erfolgreiche Aktionen"""
    message = f"SUCCESS: {action}"
    if details:
        message += f" - {details}"
    log_story("✅", message)

def log_warning(warning: str, details: str = ""):
    """Loggt Warnungen"""
    message = f"WARNING: {warning}"
    if details:
        message += f" - {details}"
    log_story("⚠️", message)

def log_startup_step(step: str, status: str = ""):
    """Loggt Startup-Schritte"""
    message = f"Startup: {step}"
    if status:
        message += f" - {status}"
    log_story("🚀", message)

def log_connection(service: str, status: str, details: str = ""):
    """Loggt Verbindungsstatus"""
    message = f"Connection to {service}: {status}"
    if details:
        message += f" - {details}"
    if status.lower() in ["connected", "success", "established"]:
        log_story("🔗", message)
    elif status.lower() in ["failed", "error", "disconnected"]:
        log_story("💔", message)
    else:
        log_story("🔄", message)
