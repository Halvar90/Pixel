# src/utils/emoji_manager.py
import os
import asyncio
import aiofiles
from pathlib import Path
from typing import Dict, Optional, List
import discord
from discord.ext import commands
import logging

logger = logging.getLogger(__name__)

class EmojiManager:
    """Verwaltet das automatische Hochladen und Caching von Emojis aus dem assets/emojis/ Ordner."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.emoji_cache: Dict[str, discord.Emoji] = {}
        self.assets_path = Path("assets/emojis")
        self.guild_id: Optional[int] = None
    
    async def initialize(self, guild_id: int):
        """Initialisiert den Emoji-Manager mit einer bestimmten Guild."""
        self.guild_id = guild_id
        await self.load_and_sync_emojis()
    
    async def load_and_sync_emojis(self):
        """Lädt alle Emoji-Dateien und synchronisiert sie mit Discord."""
        if not self.guild_id:
            logger.error("Guild ID nicht gesetzt. EmojiManager kann nicht initialisiert werden.")
            return
        
        guild = self.bot.get_guild(self.guild_id)
        if not guild:
            logger.error(f"Guild mit ID {self.guild_id} nicht gefunden.")
            return
        
        logger.info("🎭 Starte Emoji-Synchronisation...")
        
        # Alle PNG-Dateien im emojis-Ordner finden
        emoji_files = self._find_emoji_files()
        
        # Bestehende Guild-Emojis laden
        existing_emojis = {emoji.name: emoji for emoji in guild.emojis}
        
        # Neue Emojis hochladen
        uploaded_count = 0
        for file_path, emoji_name in emoji_files:
            if emoji_name not in existing_emojis:
                try:
                    emoji = await self._upload_emoji(guild, file_path, emoji_name)
                    if emoji:
                        self.emoji_cache[emoji_name] = emoji
                        uploaded_count += 1
                        logger.info(f"✅ Emoji '{emoji_name}' hochgeladen")
                    
                    # Rate Limit beachten (Discord erlaubt max 50 Emojis pro 10 Minuten)
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"❌ Fehler beim Hochladen von '{emoji_name}': {e}")
            else:
                # Bestehende Emojis in Cache laden
                self.emoji_cache[emoji_name] = existing_emojis[emoji_name]
        
        logger.info(f"🎭 Emoji-Synchronisation abgeschlossen. {uploaded_count} neue Emojis hochgeladen.")
        logger.info(f"📊 Insgesamt {len(self.emoji_cache)} Emojis verfügbar.")
    
    def _find_emoji_files(self) -> List[tuple]:
        """Findet alle PNG-Dateien im emojis-Ordner und extrahiert die Namen."""
        emoji_files = []
        
        if not self.assets_path.exists():
            logger.warning(f"Assets-Ordner '{self.assets_path}' existiert nicht.")
            return emoji_files
        
        # Rekursiv alle PNG-Dateien finden
        for png_file in self.assets_path.rglob("*.png"):
            # Emoji-Name aus Dateiname extrahieren (ohne .png)
            emoji_name = png_file.stem.lower()
            
            # Discord-Emoji-Namen müssen bestimmte Regeln befolgen
            emoji_name = self._sanitize_emoji_name(emoji_name)
            
            emoji_files.append((png_file, emoji_name))
        
        return emoji_files
    
    def _sanitize_emoji_name(self, name: str) -> str:
        """Bereinigt den Emoji-Namen für Discord-Kompatibilität."""
        # Nur Buchstaben, Zahlen und Unterstriche erlaubt
        import re
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        
        # Muss mit Buchstabe oder Unterstrich beginnen
        if sanitized and sanitized[0].isdigit():
            sanitized = f"item_{sanitized}"
        
        # Länge begrenzen (max 32 Zeichen)
        return sanitized[:32]
    
    async def _upload_emoji(self, guild: discord.Guild, file_path: Path, emoji_name: str) -> Optional[discord.Emoji]:
        """Lädt ein einzelnes Emoji in die Guild hoch."""
        try:
            async with aiofiles.open(file_path, 'rb') as f:
                emoji_data = await f.read()
            
            # Dateigröße prüfen (Discord Limit: 256KB)
            if len(emoji_data) > 256 * 1024:
                logger.warning(f"⚠️ Emoji '{emoji_name}' ist zu groß ({len(emoji_data)} bytes). Max: 256KB")
                return None
            
            emoji = await guild.create_custom_emoji(
                name=emoji_name,
                image=emoji_data,
                reason=f"Auto-Upload via Pixel Bot: {file_path.name}"
            )
            
            return emoji
            
        except discord.HTTPException as e:
            if e.status == 400 and "Maximum number of emojis reached" in str(e):
                logger.error("❌ Maximum Anzahl an Emojis in der Guild erreicht!")
            else:
                logger.error(f"❌ HTTP-Fehler beim Hochladen von '{emoji_name}': {e}")
        except Exception as e:
            logger.error(f"❌ Unerwarteter Fehler beim Hochladen von '{emoji_name}': {e}")
        
        return None
    
    def get_emoji(self, name: str) -> str:
        """Gibt den Discord-Emoji-String für einen Namen zurück."""
        try:
            emoji_name = self._sanitize_emoji_name(name.lower())
            
            if emoji_name in self.emoji_cache:
                emoji = self.emoji_cache[emoji_name]
                return f"<:{emoji.name}:{emoji.id}>"
            
            # Fallback zu Unicode-Emoji oder Text
            fallback_emojis = {
                "mana": "⚡",
                "pixel": "💎", 
                "coins": "🪙",
                "health": "❤️",
                "unknown": "❓",
                "error": "❌",
                "success": "✅",
                "warning": "⚠️",
                "info": "ℹ️"
            }
            
            return fallback_emojis.get(emoji_name, f":{name}:")
        except Exception as e:
            logger.error(f"Fehler beim Abrufen von Emoji '{name}': {e}")
            return f":{name}:"
    
    def get_emoji_list(self) -> List[str]:
        """Gibt eine Liste aller verfügbaren Emoji-Namen zurück."""
        return list(self.emoji_cache.keys())
    
    async def reload_emojis(self):
        """Lädt alle Emojis neu (nützlich für Entwicklung)."""
        self.emoji_cache.clear()
        await self.load_and_sync_emojis()

# Globale Instanz für einfachen Zugriff
emoji_manager: Optional[EmojiManager] = None

def get_emoji(name: str) -> str:
    """Hilfsfunktion für einfachen Zugriff auf Emojis."""
    try:
        if emoji_manager and emoji_manager.guild_id:
            result = emoji_manager.get_emoji(name)
            return result if result else f":{name}:"
        
        # Fallback zu Unicode-Emojis wenn Manager nicht verfügbar
        fallback_emojis = {
            "mana": "⚡",
            "pixel": "💎", 
            "coins": "🪙",
            "health": "❤️",
            "unknown": "❓",
            "error": "❌",
            "success": "✅",
            "warning": "⚠️",
            "info": "ℹ️"
        }
        
        return fallback_emojis.get(name.lower(), f":{name}:")
    except Exception as e:
        logger.error(f"Fehler in get_emoji('{name}'): {e}")
        return f":{name}:"
