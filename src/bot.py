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

# Lokale Imports
from .utils.emoji_manager import EmojiManager, emoji_manager
from .utils.logger import setup_logging

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
        
        # Slash Commands synchronisieren
        try:
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
    # Logging setup
    setup_logging()
    
    # Bot Token prüfen
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        logging.error("❌ DISCORD_TOKEN nicht in Umgebungsvariablen gefunden!")
        sys.exit(1)
    
    # Bot erstellen und starten
    bot = PixelBot()
    
    try:
        await bot.start(token)
    except KeyboardInterrupt:
        logging.info("🛑 Bot durch KeyboardInterrupt gestoppt")
    except Exception as e:
        logging.error(f"❌ Unerwarteter Fehler: {e}")
    finally:
        await bot.close()
        logging.info("👋 Bot wurde heruntergefahren")

if __name__ == "__main__":
    asyncio.run(main())
