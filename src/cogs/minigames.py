# Platzhalter - Frage des Tages, Emoji-Quiz

import discord
from discord.ext import commands

class MinigamesCog(commands.Cog):
    """Minigames wie Frage des Tages und Emoji-Quiz"""
    
    def __init__(self, bot):
        self.bot = bot

async def setup(bot):
    """Setup-Funktion für das Minigames Cog"""
    await bot.add_cog(MinigamesCog(bot))
