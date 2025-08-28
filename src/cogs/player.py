# Platzhalter - /profil, /daily

import discord
from discord.ext import commands

class PlayerCog(commands.Cog):
    """Player-Funktionen wie Profil und Daily"""
    
    def __init__(self, bot):
        self.bot = bot

async def setup(bot):
    """Setup-Funktion für das Player Cog"""
    await bot.add_cog(PlayerCog(bot))
