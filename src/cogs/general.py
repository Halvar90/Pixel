# src/cogs/general.py
import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime

from ..utils.emoji_manager import get_emoji

class GeneralCog(commands.Cog):
    """Allgemeine Bot-Commands."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @app_commands.command(name="ping", description="Zeigt die Bot-Latenz an")
    async def ping(self, interaction: discord.Interaction):
        """Einfacher Ping-Command."""
        latency = round(self.bot.latency * 1000)
        
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"⚡ Latenz: **{latency}ms**",
            color=discord.Color.green() if latency < 100 else discord.Color.yellow()
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="help", description="Zeigt alle verfügbaren Commands an")
    async def help(self, interaction: discord.Interaction):
        """Hilfe-Command mit Emoji-Showcase."""
        embed = discord.Embed(
            title=f"{get_emoji('pixel')} Pixel Bot - Hilfe",
            description="🌟 Willkommen im magischen Hain! Hier sind alle verfügbaren Commands:",
            color=discord.Color.blue()
        )
        
        # Allgemeine Commands
        embed.add_field(
            name="🎮 Allgemein",
            value=f"""
            {get_emoji('mana')} `/ping` - Bot-Latenz prüfen
            {get_emoji('pixel')} `/help` - Diese Hilfe anzeigen
            """,
            inline=False
        )
        
        # Spieler Commands
        embed.add_field(
            name="👤 Spieler",
            value=f"""
            `/profil` - Dein Spielerprofil anzeigen
            `/erkunden` - Den Hain erkunden
            `/minigame` - Ein schnelles Minispiel spielen
            """,
            inline=False
        )
        
        # Admin Commands (nur für Admins sichtbar)
        if interaction.user.guild_permissions.administrator:
            embed.add_field(
                name="🔧 Admin",
                value="""
                `/emoji_sync` - Emojis synchronisieren
                `/emoji_list` - Alle Emojis anzeigen
                `/bot_info` - Bot-Informationen
                """,
                inline=False
            )
        
        embed.set_footer(
            text=f"Bot erstellt von Halvar90 • {datetime.now().strftime('%Y')}"
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="status", description="Zeigt den Bot-Status an")
    async def status(self, interaction: discord.Interaction):
        """Bot-Status Command."""
        embed = discord.Embed(
            title=f"{get_emoji('pixel')} Bot-Status",
            color=discord.Color.green()
        )
        
        # Basis-Informationen
        embed.add_field(
            name="📊 Statistiken",
            value=f"""
            🏠 **Server:** {len(self.bot.guilds)}
            👥 **User:** {len(self.bot.users)}
            ⚡ **Latenz:** {round(self.bot.latency * 1000)}ms
            """,
            inline=True
        )
        
        # Emoji-Informationen
        from ..utils.emoji_manager import emoji_manager
        if emoji_manager:
            emoji_count = len(emoji_manager.get_emoji_list())
            embed.add_field(
                name="🎭 Emojis",
                value=f"""
                📦 **Verfügbar:** {emoji_count}
                ✅ **Status:** Online
                """,
                inline=True
            )
        
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.timestamp = datetime.now()
        
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(GeneralCog(bot))
