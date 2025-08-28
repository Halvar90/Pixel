from ..core.database import db
from typing import Optional

class Player:
    """Repräsentiert einen Spieler und seine Daten im Spiel."""
    def __init__(self, user_id: int):
        self.user_id = user_id
        # Spieler-Werte
        self.mana_current: int = 100
        self.mana_max: int = 100
        self.pixel_balance: int = 0
        # Charakter-Aussehen
        self.character_description: Optional[str] = None
        self.character_image_url: Optional[str] = None
        # Seelentier
        self.soul_animal_form: Optional[str] = None

    @classmethod
    async def get_player(cls, user_id: int) -> Optional["Player"]:
        """Lädt einen Spieler aus der DB, gibt aber None zurück, wenn er nicht existiert."""
        async with db.pool.acquire() as conn:
            player_data = await conn.fetchrow("SELECT * FROM players WHERE user_id = $1", user_id)
            if not player_data:
                return None
            
            player = cls(user_id)
            player.mana_current = player_data['mana_current']
            player.mana_max = player_data['mana_max']
            player.pixel_balance = player_data['pixel_balance']

            appearance_data = await conn.fetchrow("SELECT description, image_url FROM character_appearance WHERE player_id = $1", user_id)
            if appearance_data:
                player.character_description = appearance_data['description']
                player.character_image_url = appearance_data['image_url']
            
            soul_animal_data = await conn.fetchrow("SELECT determined_form, override_form FROM soul_animals WHERE player_id = $1", user_id)
            if soul_animal_data:
                # Die Admin-Einstellung hat immer Vorrang
                player.soul_animal_form = soul_animal_data['override_form'] or soul_animal_data['determined_form']

            return player

    @classmethod
    async def create_player(cls, user_id: int, description: str, soul_form: str, image_url: Optional[str] = None) -> "Player":
        """Erstellt einen neuen Spieler, seine Charakterbeschreibung und sein Seelentier in der DB."""
        async with db.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute("INSERT INTO players (user_id) VALUES ($1) ON CONFLICT (user_id) DO NOTHING", user_id)
                await conn.execute("INSERT INTO character_appearance (player_id, description, image_url) VALUES ($1, $2, $3)", user_id, description, image_url)
                await conn.execute("INSERT INTO soul_animals (player_id, determined_form) VALUES ($1, $2)", user_id, soul_form)
        
        player = cls(user_id)
        player.character_description = description
        player.soul_animal_form = soul_form
        player.character_image_url = image_url
        return player

    async def save(self):
        """Speichert den aktuellen Zustand des Spielers (Mana, Pixel etc.) in der Datenbank."""
        async with db.pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE players 
                SET mana_current = $1, mana_max = $2, pixel_balance = $3
                WHERE user_id = $4
                """,
                self.mana_current, self.mana_max, self.pixel_balance, self.user_id
            )
            
    async def set_character_image(self, image_url: str):
        """Aktualisiert die Bild-URL des Charakters in der Datenbank."""
        self.character_image_url = image_url
        async with db.pool.acquire() as conn:
            await conn.execute("UPDATE character_appearance SET image_url = $1 WHERE player_id = $2", image_url, self.user_id)
