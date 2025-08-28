import discord
from discord.ext import commands, tasks
import datetime
from database import get_pool
from lifecycle import log_fdt_action, log_error, log_success

# Feste Channel-IDs für FdT-System
FDT_CHANNEL_ID = 1410229292230508595  # FdT-Channel (feste ID)
MAIN_CHAT_CHANNEL_ID = 1270678012341387268  # Hauptchat für Benachrichtigungen

class MiniGames(commands.Cog):
    """Cog für die automatische Frage des Tages."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.current_fdt_id = None  # Aktuelle Frage-ID
        self.current_fdt_thread = None  # Aktueller Thread

    async def cog_load(self):
        """Wird aufgerufen wenn der Cog geladen wird."""
        print("🎮 MiniGames Cog loaded!")
        
        # Starte die tägliche FdT-Task
        if not self.daily_question_task.is_running():
            self.daily_question_task.start()
            print("⏰ Tägliche FdT-Task gestartet")

    def cog_unload(self):
        """Wird aufgerufen wenn der Cog entladen wird."""
        self.daily_question_task.cancel()
        print("🛑 Tägliche FdT-Task gestoppt")

    @tasks.loop(time=datetime.time(hour=9, minute=0))  # Täglich um 9:00 Uhr
    async def daily_question_task(self):
        """Postet täglich eine neue Frage des Tages mit Thread und Cross-Channel-Benachrichtigung."""
        try:
            fdt_channel = self.bot.get_channel(FDT_CHANNEL_ID)
            main_channel = self.bot.get_channel(MAIN_CHAT_CHANNEL_ID)
            
            if not fdt_channel:
                print(f"❌ FdT-Kanal mit ID {FDT_CHANNEL_ID} nicht gefunden!")
                return
                
            if not main_channel:
                print(f"❌ Hauptchat-Kanal mit ID {MAIN_CHAT_CHANNEL_ID} nicht gefunden!")

            pool = await get_pool()
            async with pool.acquire() as conn:
                # Hole eine zufällige unbenutzte Frage
                question_record = await conn.fetchrow("""
                    SELECT question_id, question_text 
                    FROM fdt_questions 
                    WHERE used_at IS NULL 
                    ORDER BY RANDOM() 
                    LIMIT 1
                """)
                
                if question_record:
                    self.current_fdt_id = question_record['question_id']
                    question_text = question_record['question_text']
                    
                    # Markiere Frage als verwendet
                    await conn.execute(
                        "UPDATE fdt_questions SET used_at = NOW() WHERE question_id = $1", 
                        self.current_fdt_id
                    )

                    # Erstelle das Embed für die Frage
                    embed = discord.Embed(
                        title="❓ Frage des Tages",
                        description=f"**{question_text}**",
                        color=discord.Color.blue()
                    )
                    embed.set_footer(text=f"Frage #{self.current_fdt_id} • Diskussion im Thread")
                    
                    # Sende die Frage in den FdT-Channel
                    fdt_message = await fdt_channel.send(embed=embed)
                    
                    # Erstelle einen Thread für Diskussionen
                    thread_name = f"💬 Frage #{self.current_fdt_id}"
                    try:
                        thread = await fdt_message.create_thread(
                            name=thread_name,
                            auto_archive_duration=1440  # 24 Stunden
                        )
                        self.current_fdt_thread = thread
                        
                        # Willkommensnachricht im Thread
                        welcome_embed = discord.Embed(
                            title="💬 Diskussion zur Frage des Tages",
                            description=f"**{question_text}**\n\nTeilt hier eure Gedanken und Antworten mit!",
                            color=discord.Color.green()
                        )
                        await thread.send(embed=welcome_embed)
                        
                        print(f"🧵 Thread erstellt: {thread.name} (ID: {thread.id})")
                        
                    except Exception as thread_error:
                        print(f"⚠️ Thread-Erstellung fehlgeschlagen: {thread_error}")
                        self.current_fdt_thread = None
                    
                    # Füge Reaktionen hinzu
                    await fdt_message.add_reaction("❓")
                    await fdt_message.add_reaction("💭")
                    
                    # Sende Benachrichtigung in den Hauptchat
                    if main_channel:
                        try:
                            notification_embed = discord.Embed(
                                title="📢 Neue Frage des Tages!",
                                description=f"[📍 Zur Frage springen]({fdt_message.jump_url})",
                                color=discord.Color.gold()
                            )
                            
                            await main_channel.send(embed=notification_embed)
                            print(f"📢 Benachrichtigung in Hauptchat gesendet")
                            
                        except Exception as notification_error:
                            print(f"⚠️ Hauptchat-Benachrichtigung fehlgeschlagen: {notification_error}")
                    
                    log_fdt_action("daily_question_posted", "SYSTEM", self.current_fdt_id, f"Question: {question_text[:50]}...")
                    print(f"✅ Neue Frage des Tages (ID: {self.current_fdt_id}) gepostet mit Thread.")
                    
                else:
                    # Keine Fragen mehr verfügbar
                    self.current_fdt_id = None
                    self.current_fdt_thread = None
                    embed = discord.Embed(
                        title="😅 Keine Fragen mehr!",
                        description="Mir sind die Fragen für die 'Frage des Tages' ausgegangen!\n\nEin Admin muss neue Fragen hinzufügen.",
                        color=discord.Color.orange()
                    )
                    
                    await fdt_channel.send(embed=embed)
                    print("⚠️ Keine unbenutzten Fragen mehr für FdT gefunden.")
                    
        except Exception as e:
            log_error("Daily question task failed", str(e))
            print(f"❌ Fehler bei der täglichen FdT-Task: {e}")

    @daily_question_task.before_loop
    async def before_daily_task(self):
        """Wartet bis der Bot bereit ist bevor die Task startet."""
        await self.bot.wait_until_ready()
        print("⏰ Tägliche FdT-Task bereit, wartet auf den nächsten Zyklus (täglich 9:00 Uhr)")

    @daily_question_task.error
    async def daily_task_error(self, error):
        """Error Handler für die tägliche Task."""
        log_error("Daily question task error", str(error))
        print(f"❌ Fehler in der täglichen FdT-Task: {error}")

    # Manual trigger für Testing (nur für Admins)
    @commands.command(name="trigger_fdt", hidden=True)
    @commands.has_permissions(administrator=True)
    async def trigger_fdt_manually(self, ctx):
        """Manueller Trigger für die FdT (nur für Testing)."""
        await self.daily_question_task()
        await ctx.send("✅ FdT-Task manuell ausgelöst!")

async def setup(bot: commands.Bot):
    """Setup-Funktion für den Cog."""
    cog = MiniGames(bot)
    await bot.add_cog(cog)
    print("🎮 MiniGames Cog loaded successfully")
