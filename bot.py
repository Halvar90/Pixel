import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv
from database import init_db

async def main():
    """Hauptfunktion zum Initialisieren und Starten des Bots."""
    # Lade Umgebungsvariablen (wichtig für den lokalen Test)
    load_dotenv()

    # Initialisiere die Datenbankverbindung und Tabellen
    await init_db()

    # Hole den Bot-Token
    BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    if not BOT_TOKEN:
        print("Fehler: DISCORD_BOT_TOKEN wurde nicht in der Umgebung gefunden.")
        return

    # Definiere die Discord Intents (Berechtigungen, die der Bot vom Gateway anfordert)
    intents = discord.Intents.default()
    intents.message_content = True 

    # Erstelle die Bot-Instanz
    bot = commands.Bot(command_prefix="!", intents=intents)

    # Event-Listener für den Bot-Start
    @bot.event
    async def on_ready():
        print(f'Erfolgreich eingeloggt als {bot.user}')
        
        # Lade alle Cogs aus dem 'cogs'-Verzeichnis
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                try:
                    await bot.load_extension(f'cogs.{filename[:-3]}')
                    print(f'> Cog "{filename[:-3]}" wurde geladen.')
                except Exception as e:
                    print(f'Fehler beim Laden von Cog {filename}: {e}')
        
        # Synchronisiere alle App-Commands (Slash-Befehle) mit Discord
        try:
            synced = await bot.tree.sync()
            print(f"> {len(synced)} Slash-Command(s) wurden synchronisiert.")
        except Exception as e:
            print(f"Fehler beim Synchronisieren der Commands: {e}")

    # Starte den Bot
    await bot.start(BOT_TOKEN)

# Führe die Hauptfunktion aus
if __name__ == "__main__":
    asyncio.run(main())
