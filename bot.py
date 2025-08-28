import os
import asyncio
import signal
import discord
from discord.ext import commands
from dotenv import load_dotenv
from database import init_db, close_pool
from lifecycle import (
    setup_logging, log_bot_event, log_system_event, log_startup_step, 
    log_connection, log_error, log_success, log_command_usage, log_warning
)

# Setup das Logging-System
setup_logging()

class PixelBot(commands.Bot):
    def __init__(self):
        log_startup_step("Initializing Pixel Bot")
        
        # Define Discord Intents
        intents = discord.Intents.default()
        intents.message_content = True
        
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None  # Custom help command later
        )
        
        # Railway optimization: Graceful shutdown handler
        self.setup_signal_handlers()
        log_startup_step("Signal handlers configured")
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown on Railway."""
        if os.name != 'nt':  # Not Windows
            signal.signal(signal.SIGTERM, self.handle_shutdown)
            signal.signal(signal.SIGINT, self.handle_shutdown)
            log_system_event("Signal handlers registered", "SIGTERM and SIGINT")
    
    def handle_shutdown(self, signum, frame):
        """Handle shutdown signals gracefully."""
        log_system_event(f"Received shutdown signal {signum}", "Initiating graceful shutdown")
        asyncio.create_task(self.close())
    
    async def setup_hook(self):
        """This is called when the bot is starting up."""
        log_startup_step("Running setup hook")
        
        # Initialize database
        try:
            log_startup_step("Initializing database")
            await init_db()
            log_success("Database initialized successfully")
            
            # Initialize connection pool
            log_startup_step("Creating database connection pool")
            from database import get_pool
            self.pool = await get_pool()
            log_success("Database connection pool created")
            
        except Exception as e:
            log_error("Database initialization failed", str(e))
            raise e
        
        # Load all cogs
        await self.load_cogs()
        
        # Sync slash commands
        try:
            log_startup_step("Syncing slash commands")
            synced = await self.tree.sync()
            log_success(f"Synced {len(synced)} slash command(s)")
        except Exception as e:
            log_error("Failed to sync commands", str(e))
    
    async def load_cogs(self):
        """Load all cogs from the cogs directory."""
        log_startup_step("Loading cogs")
        cogs_loaded = 0
        
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py') and filename != '__init__.py':
                try:
                    await self.load_extension(f'cogs.{filename[:-3]}')
                    log_success(f"Loaded cog: {filename[:-3]}")
                    cogs_loaded += 1
                except Exception as e:
                    log_error(f"Failed to load cog {filename}", str(e))
        
        log_startup_step(f"Cog loading complete", f"{cogs_loaded} cogs loaded")
    
    async def on_ready(self):
        """Called when the bot is ready."""
        log_bot_event("Bot successfully logged in", f"User: {self.user}")
        log_bot_event("Bot connection details", f"ID: {self.user.id}")
        log_bot_event("Guild information", f"Connected to {len(self.guilds)} guild(s)")
        
        # Log guild details
        for guild in self.guilds:
            log_bot_event(f"Connected to guild", f"'{guild.name}' (ID: {guild.id}, Members: {guild.member_count})")
        
        # Set bot activity
        activity = discord.Game(name="Pixel Adventures | /help")
        await self.change_presence(activity=activity)
        log_bot_event("Bot status set", "Pixel Adventures | /help")
        
        # Log environment information
        env = os.getenv('RAILWAY_ENVIRONMENT', 'development')
        log_system_event("Environment detected", env)
        
        log_success("Bot is fully operational and ready to serve!")
    
    async def on_command(self, ctx):
        """Log command usage."""
        guild_name = ctx.guild.name if ctx.guild else "DM"
        log_command_usage(
            command=ctx.command.name,
            user=f"{ctx.author.name}#{ctx.author.discriminator}",
            guild=guild_name,
            details=f"Channel: {ctx.channel.name if hasattr(ctx.channel, 'name') else 'DM'}"
        )
    
    async def on_application_command(self, interaction):
        """Log slash command usage."""
        guild_name = interaction.guild.name if interaction.guild else "DM"
        log_command_usage(
            command=interaction.command.name,
            user=f"{interaction.user.name}#{interaction.user.discriminator}",
            guild=guild_name,
            details=f"Channel: {interaction.channel.name if hasattr(interaction.channel, 'name') else 'DM'}"
        )
    
    async def on_error(self, event, *args, **kwargs):
        """Global error handler."""
        log_error(f"Error in event {event}", f"Args: {args}")
    
    async def on_command_error(self, ctx, error):
        """Command error handler."""
        log_error(
            f"Command error: {type(error).__name__}",
            str(error),
            user=f"{ctx.author.name}#{ctx.author.discriminator}"
        )

async def main():
    """Main function to initialize and start the bot."""
    log_startup_step("Starting Pixel Bot initialization")
    
    # Load environment variables (important for local development)
    load_dotenv()
    log_startup_step("Environment variables loaded")

    # Initialize database with retry logic
    log_startup_step("Initializing database connection")
    db_success = await init_db()
    if not db_success:
        log_error("Database initialization failed", "Exiting application")
        return
    log_success("Database initialized successfully")

    # Get bot token
    BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    if not BOT_TOKEN:
        log_error("Missing Discord bot token", "DISCORD_BOT_TOKEN not found in environment")
        return
    log_startup_step("Discord bot token verified")

    # Create and start bot
    log_startup_step("Creating bot instance")
    bot = PixelBot()
    
    try:
        log_startup_step("Connecting to Discord")
        await bot.start(BOT_TOKEN)
    except KeyboardInterrupt:
        log_system_event("Keyboard interrupt received", "Shutting down")
    except Exception as e:
        log_error("Bot crashed", str(e))
    finally:
        if not bot.is_closed():
            log_system_event("Closing bot connection")
            await bot.close()
        
        # Close database pool
        log_system_event("Closing database connection pool")
        await close_pool()
        
        log_system_event("Bot shutdown complete")

# Run the bot
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log_system_event("Application terminated by user")
