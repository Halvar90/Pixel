import discord
from discord.ext import commands

class General(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.app_commands.command(name="ping", description="Zeigt die aktuelle Latenz des Bots an.")
    async def ping(self, interaction: discord.Interaction):
        """Ein einfacher Test-Befehl."""
        latency = round(self.bot.latency * 1000)
        await interaction.response.send_message(f"Pong! 🏓 Meine Latenz beträgt {latency}ms.")

async def setup(bot: commands.Bot):
    """Diese Funktion wird von discord.py aufgerufen, um den Cog zu laden."""
    await bot.add_cog(General(bot))
