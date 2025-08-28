# src/bot.py
import asyncio
import os
import sys
import signal
import logging
from pathlib import Path

import discord
from discord.ext import commands
from dotenv import load_dotenv

# Enhanced Logging System
from .utils.logger import (
    setup_logging, 
    create_progress_logger,
    log_startup_step,
    log_cog_loading,
    log_system_status,
    log_command_sync,
    log_bot_ready
)

# Lokale Imports
from .utils.emoji_manager import EmojiManager, emoji_manager

# Imports für intelligente Systeme
from .systems import initialize_intelligent_systems
from .systems.command_registration_system import CommandRegistrationSystem

# Umgebungsvariablen laden
load_dotenv()

class PixelBot(commands.Bot):
    """Haupt-Bot-Klasse für den Pixel Discord Bot."""
    
    def __init__(self):
        # Bot-Setup mit Intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.emojis_and_stickers = True
        
        super().__init__(
            command_prefix='!',  # Fallback für Text-Commands
            intents=intents,
            help_command=None  # Eigenes Help-System
        )
        
        # Emoji-Manager initialisieren
        self.emoji_manager = EmojiManager(self)
        
        # Guild ID für Emojis (aus Umgebungsvariablen)
        self.main_guild_id = int(os.getenv('MAIN_GUILD_ID', '0'))
        
        # Graceful Shutdown Setup
        self._setup_signal_handlers()
    
    def _setup_signal_handlers(self):
        """Setup für graceful shutdown bei SIGTERM (Railway)."""
        if hasattr(signal, 'SIGTERM'):
            signal.signal(signal.SIGTERM, self._signal_handler)
        if hasattr(signal, 'SIGINT'):
            signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handler für Shutdown-Signale."""
        logging.info(f"Signal {signum} empfangen. Starte graceful shutdown...")
        asyncio.create_task(self.close())
    
    async def setup_hook(self):
        """Wird ausgeführt, bevor der Bot sich zu Discord verbindet."""
        logging.info("🔧 Bot Setup wird gestartet...")
        
        # Emoji Manager nur erstellen, aber noch nicht synchronisieren
        # (Synchronisation passiert in on_ready wenn Guild-ID verfügbar ist)
        from .utils.emoji_manager import EmojiManager
        self.emoji_manager = EmojiManager(self)
        
        # Intelligente Systeme initialisieren
        try:
            from .systems import setup_systems_for_bot
            database_url = os.getenv('DATABASE_URL')
            
            if database_url:
                system_status = await setup_systems_for_bot(self, database_url)
                logging.info(f"📊 System Status: {system_status.get('overall_success', False)}")
            else:
                logging.warning("⚠️ DATABASE_URL nicht gefunden - Systeme ohne DB gestartet")
        except Exception as e:
            logging.error(f"❌ Fehler bei intelligenten Systemen: {e}")
        
        # Cogs laden
        await self._load_cogs()
        
        logging.info("✅ Bot Setup abgeschlossen.")
    
    async def on_ready(self):
        """Wird ausgeführt, wenn der Bot bereit ist."""
        logging.info(f"🤖 {self.user} ist online!")
        logging.info(f"📊 Bot ist in {len(self.guilds)} Servern aktiv")
        
        # Emoji-Manager initialisieren
        if self.main_guild_id:
            global emoji_manager
            emoji_manager = self.emoji_manager
            await self.emoji_manager.initialize(self.main_guild_id)
        else:
            logging.warning("⚠️ MAIN_GUILD_ID nicht gesetzt. Emoji-Manager wird nicht initialisiert.")
        
        # Slash Commands synchronisieren (intelligentes System nutzen wenn verfügbar)
        try:
            if hasattr(self, 'command_registration'):
                # Intelligentes Command Registration System nutzen
                sync_result = await self.command_registration.intelligent_sync()
                if sync_result["success"]:
                    logging.info(f"🧠 Intelligenter Sync: {sync_result['commands_synced']} Commands")
                else:
                    logging.info(f"🔄 Command-Sync: {sync_result['message']}")
            else:
                # Fallback auf normalen Sync
                synced = await self.tree.sync()
                logging.info(f"🔄 {len(synced)} Slash Commands synchronisiert")
        except Exception as e:
            logging.error(f"❌ Fehler beim Synchronisieren der Slash Commands: {e}")
        
        # Status setzen
        await self.change_presence(
            activity=discord.Game(name="🌟 Im magischen Hain | /help"),
            status=discord.Status.online
        )
    
    async def _load_cogs(self):
        """Lädt alle Cog-Module."""
        cog_files = [
            'src.cogs.general',
            'src.cogs.player', 
            'src.cogs.minigames',
            'src.cogs.world_hain',
            'src.cogs.admin'
        ]
        
        for cog in cog_files:
            try:
                await self.load_extension(cog)
                logging.info(f"✅ Cog geladen: {cog}")
            except Exception as e:
                logging.error(f"❌ Fehler beim Laden von {cog}: {e}")
    
    async def on_command_error(self, ctx, error):
        """Globaler Error Handler."""
        if isinstance(error, commands.CommandNotFound):
            return  # Ignoriere unbekannte Commands
        
        logging.error(f"Command Error in {ctx.command}: {error}")
        
        # User-freundliche Fehlermeldung
        await ctx.send("❌ Ein Fehler ist aufgetreten. Bitte versuche es später erneut.")

async def main():
    """Haupt-Funktion zum Starten des Bots."""
    # Enhanced Logging Setup
    setup_logging(
        level=logging.INFO,
        log_to_file=True,
        enhanced=True
    )
    
    # Progress Logger für Startup
    progress = create_progress_logger("startup")
    progress.start_section("Bot Initialisierung", "🤖")
    
    # Bot Token prüfen
    log_startup_step(1, 4, "Überprüfe Umgebungsvariablen")
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        progress.error("DISCORD_TOKEN nicht in Umgebungsvariablen gefunden!")
        sys.exit(1)
    progress.success("Bot-Token gefunden und validiert")
    
    # Bot erstellen und starten
    log_startup_step(2, 4, "Erstelle Bot-Instanz")
    bot = PixelBot()
    progress.success("Bot-Instanz erfolgreich erstellt")
    
    try:
        log_startup_step(3, 4, "Starte Bot-Verbindung zu Discord")
        await bot.start(token)
    except KeyboardInterrupt:
        progress.warning("Bot wurde durch Benutzer gestoppt (Ctrl+C)")
        logging.info("🛑 Bot wird heruntergefahren...")
    except Exception as e:
        progress.error(f"Unerwarteter Fehler beim Bot-Start: {e}")
        logging.exception("💥 Kritischer Fehler:")
    finally:
        if 'bot' in locals():
            log_startup_step(4, 4, "Schließe Bot-Verbindung sauber")
            await bot.close()
            progress.success("Bot sauber heruntergefahren")
        progress.end_section(success=True)

if __name__ == "__main__":
    asyncio.run(main())
