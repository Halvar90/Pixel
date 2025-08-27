import os
import asyncio
import signal
import logging
import discord
from discord.ext import commands
from dotenv import load_dotenv
from database import init_db

# Configure logging for Railway
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PixelBot(commands.Bot):
    def __init__(self):
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
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown on Railway."""
        if os.name != 'nt':  # Not Windows
            signal.signal(signal.SIGTERM, self.handle_shutdown)
            signal.signal(signal.SIGINT, self.handle_shutdown)
    
    def handle_shutdown(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        asyncio.create_task(self.close())
    
    async def setup_hook(self):
        """This is called when the bot is starting up."""
        logger.info("Bot is starting up...")
        
        # Load all cogs
        await self.load_cogs()
        
        # Sync slash commands
        try:
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} slash command(s)")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")
    
    async def load_cogs(self):
        """Load all cogs from the cogs directory."""
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py') and filename != '__init__.py':
                try:
                    await self.load_extension(f'cogs.{filename[:-3]}')
                    logger.info(f'Loaded cog: {filename[:-3]}')
                except Exception as e:
                    logger.error(f'Failed to load cog {filename}: {e}')
    
    async def on_ready(self):
        """Called when the bot is ready."""
        logger.info(f'Bot successfully logged in as {self.user}')
        logger.info(f'Bot ID: {self.user.id}')
        logger.info(f'Connected to {len(self.guilds)} guild(s)')
        
        # Set bot activity
        activity = discord.Game(name="Pixel Adventures | /help")
        await self.change_presence(activity=activity)
    
    async def on_error(self, event, *args, **kwargs):
        """Global error handler."""
        logger.error(f'An error occurred in event {event}', exc_info=True)

async def main():
    """Main function to initialize and start the bot."""
    # Load environment variables (important for local development)
    load_dotenv()

    # Initialize database with retry logic
    logger.info("Initializing database...")
    db_success = await init_db()
    if not db_success:
        logger.error("Failed to initialize database. Exiting...")
        return

    # Get bot token
    BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    if not BOT_TOKEN:
        logger.error("DISCORD_BOT_TOKEN not found in environment variables")
        return

    # Create and start bot
    bot = PixelBot()
    
    try:
        await bot.start(BOT_TOKEN)
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logger.error(f"Bot crashed with error: {e}", exc_info=True)
    finally:
        if not bot.is_closed():
            await bot.close()
        logger.info("Bot shutdown complete")

# Run the bot
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application terminated by user")
