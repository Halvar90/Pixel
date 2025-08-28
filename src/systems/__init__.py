"""
Integration der beiden intelligenten Systeme in den Hauptbot
Migration System + Command Registration System
"""

import asyncio
import logging
from discord.ext import commands
from .migration_system import setup_migration_system, auto_migrate_on_startup
from .command_registration_system import setup_command_registration, auto_sync_commands

logger = logging.getLogger(__name__)

async def initialize_intelligent_systems(bot: commands.Bot, database_url: str) -> dict:
    """
    Initialisiert beide intelligenten Systeme beim Bot-Start
    
    Returns:
        dict: Status beider Systeme
    """
    results = {
        "migration_system": {"status": "not_started"},
        "command_registration": {"status": "not_started"},
        "overall_success": False
    }
    
    try:
        # 1. Migration System initialisieren und ausführen
        logger.info("Starte intelligentes Migration System...")
        migration_result = await auto_migrate_on_startup(database_url)
        results["migration_system"] = migration_result
        
        if migration_result.get("status") == "success":
            logger.info("✅ Migration System erfolgreich initialisiert")
        else:
            logger.warning(f"⚠️ Migration System: {migration_result.get('message', 'Unbekannter Status')}")
        
        # 2. Command Registration System initialisieren  
        logger.info("Starte intelligentes Command Registration System...")
        command_result = await auto_sync_commands(bot)
        results["command_registration"] = command_result
        
        if command_result.get("success"):
            logger.info("✅ Command Registration System erfolgreich initialisiert")
        else:
            logger.warning(f"⚠️ Command Registration: {command_result.get('message', 'Sync nicht erforderlich')}")
        
        # Gesamtstatus ermitteln
        migration_ok = migration_result.get("status") == "success"
        commands_ok = command_result.get("success") or not command_result.get("changes_detected")
        
        results["overall_success"] = migration_ok and commands_ok
        
        if results["overall_success"]:
            logger.info("🚀 Alle intelligenten Systeme erfolgreich initialisiert!")
        else:
            logger.warning("⚠️ Einige Systeme hatten Probleme - Bot läuft trotzdem")
        
    except Exception as e:
        logger.error(f"Kritischer Fehler bei System-Initialisierung: {e}")
        results["critical_error"] = str(e)
        results["overall_success"] = False
    
    return results


async def setup_systems_for_bot(bot: commands.Bot, database_url: str):
    """
    Setup-Funktion für die Integration in bot.py
    Wird in setup_hook() aufgerufen
    """
    try:
        # Systeme initialisieren
        system_status = await initialize_intelligent_systems(bot, database_url)
        
        # System-Instanzen am Bot verfügbar machen
        if database_url:
            try:
                bot.migration_system = await setup_migration_system(database_url)
                logger.info("Migration System Instance am Bot verfügbar: bot.migration_system")
            except Exception as e:
                logger.error(f"Fehler beim Erstellen der Migration System Instance: {e}")
        
        try:
            bot.command_registration = setup_command_registration(bot)
            logger.info("Command Registration System Instance am Bot verfügbar: bot.command_registration")
        except Exception as e:
            logger.error(f"Fehler beim Erstellen der Command Registration Instance: {e}")
        
        # Status für Monitoring
        bot.system_status = system_status
        
        return system_status
        
    except Exception as e:
        logger.error(f"Kritischer Fehler beim System-Setup: {e}")
        raise
