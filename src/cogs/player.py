import discord
import random
from discord.ext import commands
from discord import app_commands
from ..game.player_manager import Player
from typing import Optional

# --- UI-Elemente für den Start-Prozess ---

class QuestionSelect(discord.ui.Select):
    def __init__(self, question_data):
        options = []
        for label, value in question_data["options"].items():
            category_name = value.capitalize()
            display_label = f"[{category_name}] {label}"
            options.append(discord.SelectOption(label=display_label, value=value))
        
        super().__init__(placeholder=question_data["question"], min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        await self.view.handle_answer(interaction, self.values[0])

class SoulAnimalQuizView(discord.ui.View):
    def __init__(self, questions, soul_animal_map, image_url: Optional[str]):
        super().__init__(timeout=600)
        self.questions = questions
        self.soul_animal_map = soul_animal_map
        self.image_url = image_url
        self.current_question_index = 0
        self.answers = {}
        self.interaction: Optional[discord.Interaction] = None

    async def start(self, interaction: discord.Interaction):
        self.interaction = interaction
        await self.show_question()

    async def show_question(self):
        question_data = self.questions[self.current_question_index]
        
        embed = discord.Embed(
            title=f"Frage {self.current_question_index + 1}/{len(self.questions)}",
            description=f"**{question_data['question']}**",
            color=discord.Color.blue()
        )
        
        self.clear_items()
        self.add_item(QuestionSelect(question_data))
            
        if self.current_question_index == 0:
            await self.interaction.response.send_message(embed=embed, view=self, ephemeral=True)
        else:
            await self.interaction.edit_original_response(embed=embed, view=self)

    async def handle_answer(self, interaction: discord.Interaction, answer_value: str):
        await interaction.response.defer()
        
        self.answers[self.current_question_index] = answer_value
        
        self.current_question_index += 1
        if self.current_question_index < len(self.questions):
            await self.show_question()
        else:
            self.stop()
            await self.finish_creation()
            
    async def finish_creation(self):
        scores = {
            "wächter": 0, "weiser": 0, "pfleger": 0, "entdecker": 0, 
            "schöpfer": 0, "mystiker": 0, "träumer": 0, "anführer": 0,
            "wildling": 0, "schelm": 0
        }
        for value in self.answers.values():
            if value in scores:
                scores[value] += 1
        
        dominant_trait = max(scores, key=scores.get)
        
        animal_pool = self.soul_animal_map.get(dominant_trait, self.soul_animal_map["wächter"])
        determined_form = random.choice(animal_pool)

        character_description = "Ein neuer Hüter mit wachen Augen und einem Herzen voller Neugier, bereit, die Geheimnisse des Hains zu entdecken."
        
        await Player.create_player(self.interaction.user.id, character_description, determined_form, self.image_url)

        embed = discord.Embed(
            title=f"Willkommen im Hain, {self.interaction.user.display_name}!",
            description=(
                "Du hast den ersten Schritt auf einem langen Pfad getan. Die Magie des Hains antwortet auf deinen Ruf.\n\n"
                "Dein Abenteuer beginnt jetzt. Nutze `/erkunden`, um die Welt zu entdecken."
            ),
            color=discord.Color.green()
        )
        embed.add_field(name="Dein Charakter", value=character_description)
        embed.add_field(name="Die Essenz deiner Seele", value=f"Tief in dir schlummert die Seele eines **{determined_form}**.", inline=False)
        if self.image_url:
            embed.set_image(url=self.image_url)
        
        self.clear_items()
        await self.interaction.edit_original_response(embed=embed, view=self)


class PlayerCog(commands.Cog, name="Player"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Quiz-Fragen und Seelentier-Map
        self.quiz_questions = [
            {"question": "Ein Sturm hat gewütet. Deine erste Priorität?", "options": {"Den Verletzten helfen": "pfleger", "Die Wege sichern": "wächter", "Den Schaden als Chance für Neues sehen": "schöpfer"}},
            {"question": "Du findest eine uralte, unbekannte Ruine. Was tust du?", "options": {"Die verborgenen Pfade erkunden": "entdecker", "Die alten Schriften studieren": "weiser", "Ihre magische Aura spüren": "mystiker"}},
            {"question": "Ein seltenes, leuchtendes Mineral liegt vor dir. Was tust du?", "options": {"Es zu etwas Nützlichem verarbeiten": "schöpfer", "Seine Eigenschaften studieren": "weiser", "Es als wunderschönen Schatz behalten": "träumer"}},
            {"question": "Ein Freund ist in Gefahr. Wie reagierst du?", "options": {"Ich stelle mich schützend vor ihn": "wächter", "Ich suche nach einer cleveren List": "schelm", "Ich spende Trost und sorge für ihn": "pfleger"}},
            {"question": "Du musst eine Gruppe durch einen gefährlichen Wald führen. Was ist dein Stil?", "options": {"Ich gehe als Erster und ebne den Weg": "anführer", "Ich folge den alten, vergessenen Pfaden": "wildling", "Ich sorge dafür, dass niemand zurückbleibt": "pfleger"}},
            {"question": "Was ist der größte Schatz des Hains?", "options": {"Das Leben, das darin wächst": "pfleger", "Die unendlichen Möglichkeiten": "träumer", "Die verborgene Magie": "mystiker"}},
            {"question": "Ein scheues Tier nähert sich dir. Wie gewinnst du sein Vertrauen?", "options": {"Mit Geduld und ruhiger Beobachtung": "weiser", "Indem ich ihm etwas Leckeres anbiete": "pfleger", "Indem ich es mit einem lustigen Spiel locke": "schelm"}},
            {"question": "Du findest eine leere Leinwand und Farben. Was malst du?", "options": {"Eine detaillierte Karte des Waldes": "entdecker", "Ein fantastisches Fabelwesen": "träumer", "Ein Porträt deines Seelentiers": "pfleger"}},
            {"question": "Welche Art von Magie fasziniert dich am meisten?", "options": {"Magie, die heilt und Leben spendet": "pfleger", "Magie, die Illusionen und Rätsel webt": "mystiker", "Magie, die die Natur formt und wachsen lässt": "schöpfer"}},
            {"question": "Wie verbringst du am liebsten einen ruhigen Tag?", "options": {"Mit dem Bauen und Basteln an neuen Ideen": "schöpfer", "Allein in den tiefsten Teilen des Waldes": "wildling", "Im Gespräch mit den Geistern des Hains": "mystiker"}}
        ]
        self.soul_animal_map = {
            "wächter": ["Moosbewachsener Wolf", "Sonnenkralle-Bär", "Erdwächter-Dachs", "Eisenwurz-Wildschwein", "Wächter-Greif"],
            "weiser": ["Sternenlicht-Eule", "Orakel-Rabe", "Weltenwanderer-Schildkröte", "Geheimnisweber-Schlange", "Liedweber-Grille"],
            "pfleger": ["Herz des Waldes-Hirsch", "Kristallhorn-Einhorn", "Flammenherz-Rotpanda", "Quellhüter-Kröte", "Harmonie-Schwan"],
            "entdecker": ["Magischer Fuchs", "Traumtänzer-Hase", "Windtänzer-Wiesel", "Himmelsstürmer-Adler", "Bernsteinharz-Eichhörnchen"],
            "schöpfer": ["Moosbart-Biber", "Nebelweber-Spinne", "Wurzelherz-Drache", "Sonnenstein-Skarabäus", "Grollender Golem"],
            "mystiker": ["Schattenfell-Luchs", "Mondschein-Motte", "Dämmerungs-Fledermaus", "Echo-Gecko", "Flüsternde Dryade"],
            "träumer": ["Blütenstaub-Schmetterling", "Sonnenstrahl-Kolibri", "Glimmerflügel-Libelle", "Traumfänger-Falke", "Seelenfeuer-Salamander"],
            "anführer": ["Waldhüter-Pferd", "Gezeitenbringer-Kranich", "Stilles Wasser-Fisch", "Uralter Waldfürst", "Der schlafende Phönix"],
            "wildling": ["Schattenwolf", "Dornenherz-Igel", "Schattenpfoten-Katze", "Eisenwurz-Wildschwein", "Traumtänzer-Hase"],
            "schelm": ["Flussgeist-Otter", "Blüten-Pixie", "Nebel-Eichhörnchen", "Wurzel-Wichtel", "Magischer Fuchs"]
        }

    @app_commands.command(name="abenteuer_starten", description="Erstelle deinen Charakter und entdecke dein Seelentier.")
    @app_commands.describe(bild="Optional: Lade direkt ein Bild für deinen Charakter hoch (PNG).")
    async def start_adventure(self, interaction: discord.Interaction, bild: Optional[discord.Attachment] = None):
        existing_player = await Player.get_player(interaction.user.id)
        if existing_player:
            await interaction.response.send_message("Du hast dein Abenteuer bereits begonnen!", ephemeral=True)
            return
        
        image_url = None
        if bild:
            if not bild.content_type or not bild.content_type.startswith('image/png'):
                await interaction.response.send_message("Fehler: Bitte lade eine PNG-Datei hoch.", ephemeral=True)
                return
            image_url = bild.url
        
        view = SoulAnimalQuizView(self.quiz_questions, self.soul_animal_map, image_url)
        await view.start(interaction)

    @app_commands.command(name="profil", description="Zeigt dein Spielerprofil an.")
    async def profile(self, interaction: discord.Interaction):
        player = await Player.get_player(interaction.user.id)
        if not player:
            await interaction.response.send_message("Du hast dein Abenteuer noch nicht begonnen! Nutze `/abenteuer_starten`.", ephemeral=True)
            return
        
        embed = discord.Embed(title=f"Profil von {interaction.user.display_name}", color=discord.Color.purple())
        embed.set_thumbnail(url=interaction.user.avatar.url if interaction.user.avatar else None)
        
        if player.character_description:
            embed.description = f"*\"{player.character_description}\"*"
        
        embed.add_field(name="Mana", value=f"{player.mana_current} / {player.mana_max}", inline=True)
        embed.add_field(name="Pixel", value=f"{player.pixel_balance} ✨", inline=True)
        if player.soul_animal_form:
            embed.add_field(name="Seelentier-Essenz", value=player.soul_animal_form, inline=False)
        
        if player.character_image_url:
            embed.set_image(url=player.character_image_url)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="charakterbild_setzen", description="Lade ein Bild für deinen Charakter hoch (muss eine PNG-Datei sein).")
    @app_commands.describe(bild="Die PNG-Bilddatei deines Charakters.")
    async def set_character_image(self, interaction: discord.Interaction, bild: discord.Attachment):
        player = await Player.get_player(interaction.user.id)
        if not player:
            await interaction.response.send_message("Du musst zuerst dein Abenteuer mit `/abenteuer_starten` beginnen.", ephemeral=True)
            return

        if not bild.content_type or not bild.content_type.startswith('image/png'):
            await interaction.response.send_message("Fehler: Bitte lade eine PNG-Datei hoch.", ephemeral=True)
            return

        await player.set_character_image(bild.url)

        embed = discord.Embed(
            title="Charakterbild aktualisiert!",
            description="Dein neues Charakterbild wurde erfolgreich gespeichert. Du kannst es mit `/profil` ansehen.",
            color=discord.Color.green()
        )
        embed.set_image(url=bild.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(PlayerCog(bot))
