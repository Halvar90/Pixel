# Pixel Discord Bot

Ein modular aufgebauter Discord-Bot mit PostgreSQL-Datenbankunterstützung, optimiert für Railway-Hosting.

## Bot-Informationen

- **Client ID**: 1410207945257390131
- **Application ID**: 1410207945257390131

## Lokale Entwicklung

### Voraussetzungen
- Python 3.13.7
- PostgreSQL-Datenbank

### Installation

1. Repository klonen:
```bash
git clone https://github.com/Halvar90/Pixel.git
cd Pixel
```

2. Virtuelle Umgebung erstellen und aktivieren:
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
```

3. Abhängigkeiten installieren:
```bash
pip install -r requirements.txt
```

4. Umgebungsvariablen konfigurieren:
Erstelle eine `.env` Datei im Projektverzeichnis mit:
```
DISCORD_BOT_TOKEN="DEIN_BOT_TOKEN"
POSTGRES_USER="DEIN_DB_BENUTZER"
POSTGRES_PASSWORD="DEIN_DB_PASSWORT"
POSTGRES_DB="pixel_bot_db"
POSTGRES_HOST="localhost"
POSTGRES_PORT="5432"
```

5. Bot starten:
```bash
python bot.py
```

## Railway Deployment

### Schritt 1: GitHub Repository erstellen
1. Erstelle ein neues GitHub Repository
2. Pushe den Code:
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/Halvar90/Pixel.git
git push -u origin main
```

### Schritt 2: Railway Projekt erstellen
1. Gehe zu [Railway.app](https://railway.app)
2. Erstelle ein neues Projekt
3. Verbinde dein GitHub Repository
4. Füge eine PostgreSQL-Datenbank hinzu

### Schritt 3: Umgebungsvariablen auf Railway setzen
Verwende die Railway CLI oder das Web-Interface:

```bash
# Railway CLI Installation
npm install -g @railway/cli

# Login
railway login

# Projekt verknüpfen
railway link

# Umgebungsvariablen setzen
railway variables set DISCORD_BOT_TOKEN="YOUR_DISCORD_BOT_TOKEN_HERE"

# PostgreSQL-Variablen werden automatisch von Railway gesetzt
```

## Projektstruktur

```
pixel-bot/
├── cogs/                   # Bot-Module
│   ├── __init__.py
│   └── general.py         # Allgemeine Befehle
├── .env                   # Lokale Umgebungsvariablen
├── .gitignore            # Git-Ignorierungsdatei
├── bot.py                # Haupt-Bot-Datei
├── database.py           # Datenbankverbindung und -setup
├── Procfile              # Railway-Deployment-Konfiguration
├── requirements.txt      # Python-Abhängigkeiten
├── runtime.txt          # Python-Version für Railway
└── README.md            # Diese Datei
```

## Datenbank-Schema

### Tabellen:
- **players**: Globale Spielerdaten (user_id, pixel_balance, global_upgrades)
- **worlds**: Verfügbare Spielwelten
- **player_world_progress**: Spieler-Fortschritt in verschiedenen Welten
- **creatures**: Kreaturen, die Spieler besitzen

## Verfügbare Befehle

- `/ping` - Zeigt die Bot-Latenz an

## Entwicklung

### Neue Cogs hinzufügen
1. Erstelle eine neue `.py` Datei in `cogs/`
2. Implementiere die Cog-Klasse
3. Füge die `setup()` Funktion hinzu
4. Der Bot lädt automatisch alle Cogs beim Start

### Datenbank erweitern
Erweitere die `init_db()` Funktion in `database.py` um neue Tabellen oder Spalten.
