-- =============================================================================
-- Pixel - Vollständiges Datenbankschema
-- Version 1.0
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Tabelle 1: players
-- Aufgabe: Speichert die Kerndaten und Währungen für jeden Spieler.
-- Dies ist die zentrale Tabelle, auf die viele andere Tabellen verweisen.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS players (
    user_id BIGINT PRIMARY KEY,
    mana_current INT DEFAULT 100 NOT NULL,
    mana_max INT DEFAULT 100 NOT NULL,
    mana_regen_rate REAL DEFAULT 2.0 NOT NULL, -- Mana pro Stunde
    pixel_balance BIGINT DEFAULT 0 NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- -----------------------------------------------------------------------------
-- Tabelle 2: character_appearance
-- Aufgabe: Speichert die visuellen und textuellen Charakter-Details.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS character_appearance (
    appearance_id SERIAL PRIMARY KEY,
    player_id BIGINT UNIQUE NOT NULL REFERENCES players(user_id) ON DELETE CASCADE,
    description TEXT,
    image_url TEXT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- -----------------------------------------------------------------------------
-- Tabelle 3: soul_animals
-- Aufgabe: Verwaltet den Zustand und die Form des Seelentiers eines Spielers.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS soul_animals (
    animal_id SERIAL PRIMARY KEY,
    player_id BIGINT UNIQUE NOT NULL REFERENCES players(user_id) ON DELETE CASCADE,
    determined_form VARCHAR(255) NOT NULL, -- Das Ergebnis des Quiz
    override_form VARCHAR(255) NULL,      -- Manuelle Zuweisung durch Admin
    current_stage INT DEFAULT 1 NOT NULL,
    friendship INT DEFAULT 0 NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- -----------------------------------------------------------------------------
-- Tabelle 4: inventory
-- Aufgabe: Speichert alle Items, die ein Spieler besitzt.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS inventory (
    inventory_id SERIAL PRIMARY KEY,
    player_id BIGINT NOT NULL REFERENCES players(user_id) ON DELETE CASCADE,
    item_id VARCHAR(255) NOT NULL, -- Eindeutige ID des Items (z.B. "kleiner_mana_kristall")
    quantity INT DEFAULT 1 NOT NULL,
    UNIQUE(player_id, item_id) -- Stellt sicher, dass jeder Spieler ein Item nur einmal im Inventar hat (Menge wird erhöht)
);

-- -----------------------------------------------------------------------------
-- Tabelle 5: grimoire_entries
-- Aufgabe: Verfolgt den Fortschritt des Spielers in den Sammelbüchern.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS grimoire_entries (
    entry_id SERIAL PRIMARY KEY,
    player_id BIGINT NOT NULL REFERENCES players(user_id) ON DELETE CASCADE,
    grimoire_id VARCHAR(255) NOT NULL, -- Eindeutige ID der Kreatur, Pflanze oder des Rezepts
    entry_type VARCHAR(50) NOT NULL,   -- 'creature', 'plant', 'recipe'
    discovery_level INT DEFAULT 1 NOT NULL, -- Für Kreaturen (1=Sichtung, 2=Studie, 3=Vertrautheit)
    UNIQUE(player_id, grimoire_id)
);

-- -----------------------------------------------------------------------------
-- Tabelle 6: daily_activity_tracker
-- Aufgabe: Zählt tägliche Aktivitäten, um Limits durchzusetzen (z.B. für Minigames).
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS daily_activity_tracker (
    activity_id SERIAL PRIMARY KEY,
    player_id BIGINT NOT NULL REFERENCES players(user_id) ON DELETE CASCADE,
    activity_type VARCHAR(100) NOT NULL, -- z.B. 'emojiquiz_win'
    activity_count INT DEFAULT 1 NOT NULL,
    activity_date DATE DEFAULT CURRENT_DATE,
    UNIQUE(player_id, activity_type, activity_date)
);

-- -----------------------------------------------------------------------------
-- Tabelle 7: active_buffs
-- Aufgabe: Speichert aktive, temporäre Boni für Spieler.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS active_buffs (
    buff_id SERIAL PRIMARY KEY,
    player_id BIGINT NOT NULL REFERENCES players(user_id) ON DELETE CASCADE,
    buff_type VARCHAR(100) NOT NULL, -- z.B. 'mana_regen_boost'
    modifier REAL NOT NULL,          -- z.B. 1.2 für einen 20% Boost
    expires_at TIMESTAMPTZ NOT NULL
);

-- -----------------------------------------------------------------------------
-- Tabellen 8 & 9: Frage des Tages (FdT)
-- Aufgabe: Speichern die Fragen und die Antworten der Spieler.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS fdt_questions (
    question_id SERIAL PRIMARY KEY,
    question_text TEXT NOT NULL UNIQUE,
    used_at TIMESTAMPTZ NULL
);

CREATE TABLE IF NOT EXISTS fdt_answers (
    answer_id SERIAL PRIMARY KEY,
    question_id INT NOT NULL REFERENCES fdt_questions(question_id) ON DELETE CASCADE,
    player_id BIGINT NOT NULL REFERENCES players(user_id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(question_id, player_id) -- Jeder Spieler kann pro Frage nur einmal antworten
);
