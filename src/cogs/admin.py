# src/cogs/admin.py
import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional

from ..utils.emoji_manager import get_emoji

class AdminCog(commands.Cog):
    """Admin-Commands für Bot-Verwaltung."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    async def cog_check(self, ctx) -> bool:
        """Überprüft, ob der User Admin-Rechte hat."""
        return ctx.author.guild_permissions.administrator
    
    def _get_emoji_manager(self):
        """Sichere Methode zum Abrufen des Emoji-Managers."""
        return getattr(self.bot, 'emoji_manager', None)
    
    @app_commands.command(name="emoji_sync", description="[ADMIN] Synchronisiert alle Emojis aus dem assets/emojis/ Ordner")
    async def emoji_sync(self, interaction: discord.Interaction):
        """Synchronisiert alle Emojis neu."""
        await interaction.response.defer(ephemeral=True)
        
        # Emoji-Manager über Bot-Instanz abrufen
        emoji_manager = self._get_emoji_manager()
        
        if not emoji_manager:
            await interaction.followup.send("❌ Emoji-Manager ist nicht initialisiert!", ephemeral=True)
            return
        
        try:
            await emoji_manager.reload_emojis()
            emoji_count = len(emoji_manager.get_emoji_list())
            
            embed = discord.Embed(
                title="Emoji-Synchronisation",
                description=f"Erfolgreich abgeschlossen!\n**{emoji_count}** Emojis verfügbar",
                color=discord.Color.green()
            )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            embed = discord.Embed(
                title="Emoji-Synchronisation", 
                description=f"Fehler: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
    
    @app_commands.command(name="emoji_list", description="[ADMIN] Zeigt alle verfügbaren Bot-Emojis an")
    async def emoji_list(self, interaction: discord.Interaction):
        """Zeigt alle verfügbaren Emojis an."""
        await interaction.response.defer(ephemeral=True)
        
        # Emoji-Manager über Bot-Instanz abrufen
        emoji_manager = self._get_emoji_manager()
        
        if not emoji_manager:
            await interaction.followup.send("❌ Emoji-Manager ist nicht initialisiert!", ephemeral=True)
            return
        
        emoji_names = emoji_manager.get_emoji_list()
        
        if not emoji_names:
            await interaction.followup.send("📭 Keine Emojis gefunden.", ephemeral=True)
            return
        
        # Emojis in Kategorien gruppieren
        categories = {}
        for name in emoji_names:
            # Erste Kategorie aus dem Namen extrahieren (z.B. "item_sword" -> "item")
            category = name.split('_')[0] if '_' in name else 'other'
            if category not in categories:
                categories[category] = []
            categories[category].append(name)
        
        embed = discord.Embed(
            title="Verfügbare Bot-Emojis",
            description=f"Insgesamt **{len(emoji_names)}** Emojis",
            color=discord.Color.blue()
        )
        
        for category, names in categories.items():
            emoji_display = []
            for name in names[:10]:  # Max 10 pro Kategorie anzeigen
                emoji_str = emoji_manager.get_emoji(name)
                emoji_display.append(f"{emoji_str} `{name}`")
            
            if len(names) > 10:
                emoji_display.append(f"... und {len(names) - 10} weitere")
            
            embed.add_field(
                name=f"{category.title()} ({len(names)})",
                value="\n".join(emoji_display) if emoji_display else "Keine",
                inline=False
            )
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    @app_commands.command(name="emoji_test", description="[ADMIN] Testet die Emoji-Anzeige")
    async def emoji_test(self, interaction: discord.Interaction, emoji_name: str):
        """Testet ein spezifisches Emoji."""
        emoji_str = get_emoji(emoji_name)
        
        embed = discord.Embed(
            title="Emoji-Test",
            description=f"**Name:** `{emoji_name}`\n**Output:** {emoji_str}",
            color=discord.Color.yellow()
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="info", description="[ADMIN] Zeigt Bot-Informationen an")
    async def show_bot_info(self, interaction: discord.Interaction):
        """Zeigt Bot-Statistiken an."""
        # Emoji-Manager über Bot-Instanz abrufen
        emoji_manager = self._get_emoji_manager()
        
        embed = discord.Embed(
            title="Bot-Informationen",
            color=discord.Color.blue()
        )
        
        # Grundlegende Stats
        embed.add_field(name="Server", value=len(self.bot.guilds), inline=True)
        embed.add_field(name="User", value=len(self.bot.users), inline=True)
        embed.add_field(name="Latenz", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        
        # Emoji Stats
        if emoji_manager:
            emoji_count = len(emoji_manager.get_emoji_list())
            embed.add_field(name="Emojis", value=emoji_count, inline=True)
        
        # Cog Stats
        embed.add_field(name="🔧 Cogs", value=len(self.bot.cogs), inline=True)
        embed.add_field(name="💬 Commands", value=len(self.bot.tree.get_commands()), inline=True)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(AdminCog(bot))
