import discord
import asyncio
import time
import os
from discord.ext import commands

class General(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.start_time = time.time()

    @discord.app_commands.command(name="ping", description="Shows the bot's current latency and status.")
    async def ping(self, interaction: discord.Interaction):
        """A simple test command with enhanced information."""
        latency = round(self.bot.latency * 1000)
        uptime = time.time() - self.start_time
        
        # Format uptime
        hours, remainder = divmod(int(uptime), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        embed = discord.Embed(
            title="🏓 Pong!",
            color=discord.Color.green()
        )
        embed.add_field(name="Latency", value=f"{latency}ms", inline=True)
        embed.add_field(name="Uptime", value=f"{hours}h {minutes}m {seconds}s", inline=True)
        embed.add_field(name="Environment", value=os.getenv('RAILWAY_ENVIRONMENT', 'development'), inline=True)
        
        await interaction.response.send_message(embed=embed)

    @discord.app_commands.command(name="status", description="Shows detailed bot status information.")
    async def status(self, interaction: discord.Interaction):
        """Shows detailed bot status for Railway monitoring."""
        embed = discord.Embed(
            title="🤖 Bot Status",
            color=discord.Color.blue()
        )
        
        # Bot information
        embed.add_field(name="Bot Name", value=self.bot.user.name, inline=True)
        embed.add_field(name="Bot ID", value=self.bot.user.id, inline=True)
        embed.add_field(name="Servers", value=len(self.bot.guilds), inline=True)
        
        # Performance metrics
        latency = round(self.bot.latency * 1000)
        embed.add_field(name="Latency", value=f"{latency}ms", inline=True)
        
        # Environment info
        env = os.getenv('RAILWAY_ENVIRONMENT', 'development')
        embed.add_field(name="Environment", value=env, inline=True)
        
        # Database status (simple check)
        try:
            from database import get_db_connection
            conn = await get_db_connection()
            await conn.close()
            db_status = "✅ Connected"
        except Exception:
            db_status = "❌ Error"
        
        embed.add_field(name="Database", value=db_status, inline=True)
        
        await interaction.response.send_message(embed=embed)

    @discord.app_commands.command(name="help", description="Shows available commands and bot information.")
    async def help_command(self, interaction: discord.Interaction):
        """Custom help command."""
        embed = discord.Embed(
            title="🎮 Pixel Bot - Help",
            description="Welcome to Pixel Bot! A modular Discord bot for gaming adventures.",
            color=discord.Color.purple()
        )
        
        embed.add_field(
            name="🏓 General Commands",
            value="`/ping` - Check bot latency\n`/status` - Detailed bot status\n`/help` - This help message",
            inline=False
        )
        
        embed.add_field(
            name="🔧 Bot Info",
            value=f"Version: 1.0.0\nEnvironment: {os.getenv('RAILWAY_ENVIRONMENT', 'development')}\nHosted on Railway",
            inline=False
        )
        
        embed.set_footer(text="More features coming soon!")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    """This function is called by discord.py to load the cog."""
    await bot.add_cog(General(bot))
