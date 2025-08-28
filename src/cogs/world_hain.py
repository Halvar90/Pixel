# World Hain spezifische Funktionen

import discord
from discord.ext import commands

class WorldHainCog(commands.Cog):
    """World Hain Server spezifische Funktionen"""
    
    def __init__(self, bot):
        self.bot = bot

async def setup(bot):
    """Setup-Funktion für das World Hain Cog"""
    await bot.add_cog(WorldHainCog(bot))