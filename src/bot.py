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
from .systems import setup_systems_for_bot
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
        startup_logger = logging.getLogger("startup")
        startup_logger.info("=" * 60)
        startup_logger.info("⚙️ PHASE 2: BOT-INFRASTRUKTUR")
        startup_logger.info("=" * 60)
        
        # 1. Datenbank und Cache initialisieren
        try:
            log_startup_step("[1/4] Initialisiere Datenbank-Verbindung")
            from .core.database import db
            await db.connect()
            await db.execute_schema()
            log_startup_step("✅ Datenbank verbunden und Schema geladen")
        except Exception as e:
            logging.error(f"❌ FEHLER: Datenbankverbindung fehlgeschlagen: {e}")
            
        try:
            log_startup_step("[2/4] Initialisiere Redis-Cache")
            from .core.cache import cache
            await cache.connect()
            log_startup_step("✅ Redis-Cache verbunden")
        except Exception as e:
            logging.error(f"❌ FEHLER: Redis-Verbindung fehlgeschlagen: {e}")
        
        # 2. Emoji Manager vorbereiten (noch nicht synchronisieren)
        log_startup_step("[3/4] Bereite Emoji-Manager vor")
        from .utils.emoji_manager import EmojiManager
        self.emoji_manager = EmojiManager(self)
        log_startup_step("✅ Emoji-Manager erstellt")
        
        # 3. Intelligente Systeme initialisieren
        try:
            log_startup_step("[4/4] Starte intelligente Systeme")
            from .systems import setup_systems_for_bot
            database_url = os.getenv('DATABASE_URL')
            
            if database_url:
                system_status = await setup_systems_for_bot(self, database_url)
                if system_status.get('overall_success', False):
                    log_startup_step("✅ Intelligente Systeme initialisiert")
                else:
                    log_startup_step("⚠️ Intelligente Systeme mit Warnungen gestartet")
            else:
                logging.warning("⚠️ DATABASE_URL nicht gefunden - Systeme ohne DB gestartet")
                log_startup_step("⚠️ Systeme im Fallback-Modus")
        except Exception as e:
            logging.error(f"❌ FEHLER: Problem bei intelligenten Systemen: {e}")
        
        startup_logger.info("✅ PHASE 2 ABGESCHLOSSEN - Infrastruktur bereit\n")
    
    async def on_ready(self):
        """Wird ausgeführt, wenn der Bot bereit ist."""
        startup_logger = logging.getLogger("startup")
        startup_logger.info("=" * 60)
        startup_logger.info("🎯 PHASE 3: BOT-MODULE & COMMANDS")
        startup_logger.info("=" * 60)
        
        # 1. Cogs laden
        log_startup_step("[1/4] Lade Bot-Module (Cogs)")
        await self._load_cogs()
        log_startup_step("✅ Alle Bot-Module geladen")
        
        # 2. Emoji-Manager initialisieren
        log_startup_step("[2/4] Synchronisiere Emoji-System")
        if self.main_guild_id:
            global emoji_manager
            emoji_manager = self.emoji_manager
            try:
                await self.emoji_manager.initialize(self.main_guild_id)
                log_startup_step("✅ Emoji-System synchronisiert")
            except Exception as e:
                logging.error(f"❌ Emoji-Synchronisation fehlgeschlagen: {e}")
                log_startup_step("⚠️ Emoji-System im Fallback-Modus")
        else:
            logging.warning("⚠️ MAIN_GUILD_ID nicht gesetzt - Emoji-Manager nicht verfügbar")
            log_startup_step("⚠️ Emoji-System deaktiviert")
        
        # 3. Slash Commands synchronisieren
        log_startup_step("[3/4] Synchronisiere Discord-Commands")
        try:
            if hasattr(self, 'command_registration'):
                # Intelligentes Command Registration System nutzen
                sync_result = await self.command_registration.intelligent_sync()
                if sync_result["success"]:
                    log_startup_step(f"✅ {sync_result['commands_synced']} Commands synchronisiert (intelligent)")
                else:
                    log_startup_step(f"⚠️ Command-Sync: {sync_result['message']}")
            else:
                # Fallback auf normalen Sync
                synced = await self.tree.sync()
                log_startup_step(f"✅ {len(synced)} Commands synchronisiert (standard)")
        except Exception as e:
            logging.error(f"❌ Fehler bei Command-Synchronisation: {e}")
            log_startup_step("❌ Command-Synchronisation fehlgeschlagen")
        
        # 4. Bot-Status setzen
        log_startup_step("[4/4] Setze Bot-Status")
        await self.change_presence(
            activity=discord.Game(name="🌟 Im magischen Hain | /help"),
            status=discord.Status.online
        )
        log_startup_step("✅ Bot-Status gesetzt")
        
        startup_logger.info("✅ PHASE 3 ABGESCHLOSSEN - Commands bereit\n")
        
        # ================================
        # 🌟 PHASE 4: BOT READY & ONLINE  
        # ================================
        startup_logger.info("=" * 60)
        startup_logger.info("🌟 PHASE 4: BOT VOLLSTÄNDIG BEREIT")
        startup_logger.info("=" * 60)
        
        startup_logger.info(f"🤖 {self.user} ist erfolgreich online!")
        startup_logger.info(f"📊 Aktiv in {len(self.guilds)} Server(n)")
        startup_logger.info(f"👥 Erreicht {len(self.users)} Benutzer")
        startup_logger.info("🎮 Alle Systeme funktionsfähig - Bot bereit für Commands!")
        
        startup_logger.info("=" * 60)
        startup_logger.info("🚀 PIXEL BOT ERFOLGREICH GESTARTET!")
        startup_logger.info("=" * 60)
        startup_logger.info("")
    
    async def _load_cogs(self):
        """Lädt alle Cog-Module."""
        cog_files = [
            'src.cogs.general',
            'src.cogs.player', 
            'src.cogs.minigames',
            'src.cogs.world_hain',
            'src.cogs.admin'
        ]
        
        cogs_logger = logging.getLogger("cogs")
        for i, cog in enumerate(cog_files, 1):
            try:
                await self.load_extension(cog)
                cogs_logger.info(f"   ✅ [{i}/{len(cog_files)}] {cog.split('.')[-1]}")
            except Exception as e:
                cogs_logger.error(f"   ❌ [{i}/{len(cog_files)}] {cog.split('.')[-1]}: {e}")
    
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
    
    # ================================
    # 🚀 PHASE 1: GRUNDLEGENDE CHECKS
    # ================================
    startup_logger = logging.getLogger("startup")
    startup_logger.info("=" * 60)
    startup_logger.info("🚀 PHASE 1: GRUNDLEGENDE VALIDIERUNG")
    startup_logger.info("=" * 60)
    
    log_startup_step("[1/3] Überprüfe Umgebungsvariablen")
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        logging.error("❌ FATAL: DISCORD_TOKEN nicht in Umgebungsvariablen gefunden!")
        sys.exit(1)
    log_startup_step("✅ Bot-Token validiert")
    
    log_startup_step("[2/3] Überprüfe Python-Umgebung")
    log_startup_step(f"✅ Python {sys.version.split()[0]} | OS: {os.name}")
    
    log_startup_step("[3/3] Erstelle Bot-Instanz")
    try:
        bot = PixelBot()
        log_startup_step("✅ Bot-Instanz erfolgreich erstellt")
    except Exception as e:
        logging.error(f"❌ FATAL: Fehler bei Bot-Erstellung: {e}")
        sys.exit(1)
    
    startup_logger.info("✅ PHASE 1 ABGESCHLOSSEN - Starte Bot-Verbindung\n")
    
    # ================================  
    # 🔗 PHASE 2: DISCORD-VERBINDUNG
    # ================================
    # Ab hier übernimmt setup_hook() und on_ready()
    
    try:
        # Bot startet und läuft permanent bis manuell gestoppt
        await bot.start(token)
    except KeyboardInterrupt:
        logging.warning("⚠️ Bot wurde durch Benutzer gestoppt (Ctrl+C)")
        logging.info("🛑 Starte sauberes Herunterfahren...")
    except discord.LoginFailure:
        logging.error("❌ FATAL: Login fehlgeschlagen - Token ungültig!")
    except discord.HTTPException as e:
        logging.error(f"❌ FATAL: Discord HTTP Fehler: {e}")
    except Exception as e:
        logging.error(f"❌ FATAL: Unerwarteter Fehler: {e}")
        logging.exception("💥 Stack Trace:")
    finally:
        if 'bot' in locals():
            # ================================
            # 🔌 PHASE 5: SAUBERES HERUNTERFAHREN  
            # ================================
            startup_logger.info("=" * 60)
            startup_logger.info("🔌 PHASE 5: SAUBERES HERUNTERFAHREN")
            startup_logger.info("=" * 60)
            
            try:
                from .core.database import db
                from .core.cache import cache
                log_startup_step("[1/2] Schließe Datenbank und Cache")
                await db.disconnect()
                await cache.disconnect()
                log_startup_step("✅ Verbindungen geschlossen")
            except Exception as e:
                logging.error(f"❌ Fehler beim Schließen der Verbindungen: {e}")
            
            log_startup_step("[2/2] Schließe Bot-Verbindung")
            await bot.close()
            log_startup_step("✅ Bot sauber heruntergefahren")
            
            startup_logger.info("🏁 SHUTDOWN ABGESCHLOSSEN")
            startup_logger.info("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
