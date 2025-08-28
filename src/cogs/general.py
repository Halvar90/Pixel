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
        """Hilfe-Command mit aktuellen Commands."""
        embed = discord.Embed(
            title="Pixel Bot - Hilfe",
            description="Hier sind alle verfügbaren Commands:",
            color=discord.Color.blue()
        )
        
        # Allgemeine Commands
        embed.add_field(
            name="🎮 Allgemein",
            value="""
            `/ping` - Bot-Latenz prüfen
            `/help` - Diese Hilfe anzeigen
            `/status` - Bot-Status anzeigen
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
                `/info` - Bot-Informationen
                """,
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="status", description="Zeigt den Bot-Status an")
    async def status(self, interaction: discord.Interaction):
        """Bot-Status Command."""
        embed = discord.Embed(
            title="Bot-Status",
            color=discord.Color.green()
        )
        
        # Basis-Informationen
        embed.add_field(
            name="📊 Statistiken",
            value=f"""
            **Server:** {len(self.bot.guilds)}
            **User:** {len(self.bot.users)}
            **Latenz:** {round(self.bot.latency * 1000)}ms
            """,
            inline=True
        )
        
        # Emoji-Informationen
        emoji_manager = getattr(self.bot, 'emoji_manager', None)
        if emoji_manager:
            emoji_count = len(emoji_manager.get_emoji_list())
            embed.add_field(
                name="🎭 Emojis",
                value=f"""
                **Verfügbar:** {emoji_count}
                **Status:** Online
                """,
                inline=True
            )
        
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(GeneralCog(bot))
