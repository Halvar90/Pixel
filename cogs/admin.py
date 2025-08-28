import discord
from discord.ext import commands
from discord import app_commands
from database import get_pool

# Erstelle eine Befehlsgruppe für die FdT-Admin-Befehle
fdt_admin_group = app_commands.Group(name="fdt-admin", description="Admin-Befehle für die Frage des Tages.")

@fdt_admin_group.command(name="add", description="Fügt eine neue Frage des Tages hinzu.")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(frage="Der vollständige Text der neuen Frage.")
async def fdt_add(interaction: discord.Interaction, frage: str):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("INSERT INTO fdt_questions (question_text, added_by) VALUES ($1, $2)", frage, interaction.user.id)
    await interaction.response.send_message(f"✅ Frage wurde erfolgreich hinzugefügt.", ephemeral=True)

@fdt_admin_group.command(name="list", description="Zeigt alle Fragen des Tages an.")
@app_commands.checks.has_permissions(administrator=True)
async def fdt_list(interaction: discord.Interaction):
    pool = await get_pool()
    async with pool.acquire() as conn:
        questions = await conn.fetch("SELECT question_id, question_text FROM fdt_questions ORDER BY question_id ASC LIMIT 100")
    
    if not questions:
        await interaction.response.send_message("Es sind keine Fragen in der Datenbank.", ephemeral=True)
        return

    description = ""
    for q in questions:
        description += f"**ID {q['question_id']}:** {q['question_text'][:100]}...\n"
    
    embed = discord.Embed(title="Fragen des Tages", description=description, color=discord.Color.orange())
    await interaction.response.send_message(embed=embed, ephemeral=True)

@fdt_admin_group.command(name="delete", description="Löscht eine Frage des Tages anhand ihrer ID.")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(question_id="Die ID der Frage, die gelöscht werden soll.")
async def fdt_delete(interaction: discord.Interaction, question_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        result = await conn.execute("DELETE FROM fdt_questions WHERE question_id = $1", question_id)
    
    if result == "DELETE 1":
        await interaction.response.send_message(f"✅ Frage mit ID {question_id} wurde gelöscht.", ephemeral=True)
    else:
        await interaction.response.send_message(f"⚠️ Keine Frage mit ID {question_id} gefunden.", ephemeral=True)

@fdt_admin_group.command(name="stats", description="Zeigt FdT-Statistiken an.")
@app_commands.checks.has_permissions(administrator=True)
async def fdt_stats(interaction: discord.Interaction):
    pool = await get_pool()
    async with pool.acquire() as conn:
        # Statistiken sammeln
        total_questions = await conn.fetchval("SELECT COUNT(*) FROM fdt_questions")
        total_answers = await conn.fetchval("SELECT COUNT(*) FROM fdt_answers")
        active_users = await conn.fetchval("SELECT COUNT(DISTINCT user_id) FROM fdt_answers")
        recent_answers = await conn.fetchval("""
            SELECT COUNT(*) FROM fdt_answers 
            WHERE created_at >= NOW() - INTERVAL '7 days'
        """)
        
        # Top 3 aktivste Nutzer
        top_users = await conn.fetch("""
            SELECT user_id, COUNT(*) as answer_count 
            FROM fdt_answers 
            GROUP BY user_id 
            ORDER BY answer_count DESC 
            LIMIT 3
        """)
    
    embed = discord.Embed(
        title="📊 FdT Admin-Statistiken",
        color=discord.Color.blue()
    )
    
    embed.add_field(name="📝 Gesamte Fragen", value=str(total_questions), inline=True)
    embed.add_field(name="💬 Gesamte Antworten", value=str(total_answers), inline=True)
    embed.add_field(name="👥 Aktive Nutzer", value=str(active_users), inline=True)
    embed.add_field(name="📅 Antworten (7 Tage)", value=str(recent_answers), inline=True)
    
    if top_users:
        top_users_text = ""
        for i, user in enumerate(top_users, 1):
            try:
                discord_user = interaction.client.get_user(user['user_id'])
                name = discord_user.display_name if discord_user else f"User#{user['user_id']}"
            except:
                name = f"User#{user['user_id']}"
            top_users_text += f"{i}. {name}: {user['answer_count']} Antworten\n"
        
        embed.add_field(name="🏆 Top 3 Nutzer", value=top_users_text, inline=False)
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@fdt_admin_group.command(name="set-channel", description="Zeigt die konfigurierten FdT-Kanäle an.")
@app_commands.checks.has_permissions(administrator=True)
async def fdt_set_channel(interaction: discord.Interaction):
    """Zeigt die fest konfigurierten Channel-IDs an."""
    try:
        embed = discord.Embed(
            title="📺 FdT-Kanäle konfiguriert",
            description="Das FdT-System verwendet feste Channel-IDs:",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="❓ FdT-Channel", 
            value=f"<#{1410229292230508595}>\n`ID: 1410229292230508595`", 
            inline=False
        )
        embed.add_field(
            name="📢 Hauptchat (Benachrichtigungen)", 
            value=f"<#{1270678012341387268}>\n`ID: 1270678012341387268`", 
            inline=False
        )
        embed.add_field(name="⏰ Zeitplan", value="Täglich um 9:00 Uhr", inline=True)
        embed.add_field(name="🧵 Features", value="• Automatische Threads\n• Cross-Channel-Benachrichtigungen", inline=True)
        embed.set_footer(text="Channel-IDs sind fest im Code konfiguriert")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
    except Exception as e:
        embed = discord.Embed(
            title="❌ Fehler",
            description=f"Es gab einen Fehler: {str(e)}",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

@fdt_admin_group.command(name="trigger", description="Löst manuell eine neue FdT aus (für Testing).")
@app_commands.checks.has_permissions(administrator=True)
async def fdt_trigger(interaction: discord.Interaction):
    """Löst manuell eine neue FdT aus."""
    try:
        # Hole den MiniGames Cog
        minigames_cog = interaction.client.get_cog("MiniGames")
        if not minigames_cog:
            embed = discord.Embed(
                title="❌ Fehler",
                description="MiniGames Cog nicht gefunden.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        
        # Führe die tägliche Task aus
        await minigames_cog.daily_question_task()
        
        embed = discord.Embed(
            title="✅ FdT ausgelöst",
            description="Die Frage des Tages wurde manuell ausgelöst und gepostet.",
            color=discord.Color.green()
        )
        await interaction.followup.send(embed=embed, ephemeral=True)
        
    except Exception as e:
        embed = discord.Embed(
            title="❌ Fehler",
            description=f"Es gab einen Fehler beim Auslösen der FdT: {str(e)}",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed, ephemeral=True)

@fdt_admin_group.command(name="reset-questions", description="Setzt alle Fragen zurück (entfernt used_at).")
@app_commands.checks.has_permissions(administrator=True)
async def fdt_reset_questions(interaction: discord.Interaction):
    """Setzt alle Fragen zurück, damit sie wieder verwendet werden können."""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            # Zähle verwendete Fragen
            used_count = await conn.fetchval("SELECT COUNT(*) FROM fdt_questions WHERE used_at IS NOT NULL")
            
            if used_count == 0:
                embed = discord.Embed(
                    title="ℹ️ Keine Aktion nötig",
                    description="Es gibt keine verwendeten Fragen zum Zurücksetzen.",
                    color=discord.Color.blue()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # Setze alle Fragen zurück
            await conn.execute("UPDATE fdt_questions SET used_at = NULL")
            
            embed = discord.Embed(
                title="✅ Fragen zurückgesetzt",
                description=f"**{used_count}** verwendete Fragen wurden zurückgesetzt und können wieder verwendet werden.",
                color=discord.Color.green()
            )
            embed.add_field(name="💡 Info", value="Alle Fragen stehen wieder für die tägliche Auswahl zur Verfügung.", inline=False)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
    except Exception as e:
        embed = discord.Embed(
            title="❌ Fehler",
            description=f"Es gab einen Fehler beim Zurücksetzen: {str(e)}",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

async def setup(bot: commands.Bot):
    # Fügt den Cog hinzu und registriert die Befehlsgruppe global
    cog = Admin(bot)
    await bot.add_cog(cog)
    bot.tree.add_command(fdt_admin_group)
