# Pixel Discord Bot 🎮

Ein hochoptimierter, modular aufgebauter Discord-Bot mit PostgreSQL-Datenbankunterstützung, speziell optimiert für Railway-Hosting.

## 🚀 Railway-Optimierungen

- **Automatische Datenbankverbindung**: Nutzt Railway's `DATABASE_URL`
- **Graceful Shutdown**: Behandelt SIGTERM/SIGINT Signale korrekt
- **Retry-Logik**: Robuste Datenbankverbindung mit exponential backoff
- **Umfassendes Logging**: Strukturierte Logs für Railway-Monitoring
- **Connection Pooling**: Optimierte Datenbankperformance
- **Health Checks**: `/status` Command für Monitoring

## 🤖 Bot-Informationen

- **Client ID**: 1410207945257390131
- **Application ID**: 1410207945257390131
- **Repository**: https://github.com/Halvar90/Pixel

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

## 🛠️ Railway Deployment (Empfohlen)

### Schritt 1: Repository ist bereits verbunden ✅
- GitHub Repository: `https://github.com/Halvar90/Pixel`

### Schritt 2: Railway Projekt erstellen
1. Gehe zu [Railway.app](https://railway.app)
2. **"New Project"** → **"Deploy from GitHub repo"**
3. Wähle: **`Halvar90/Pixel`**
4. Railway erkennt automatisch Python und verwendet die `railway.json` Konfiguration

### Schritt 3: PostgreSQL-Datenbank hinzufügen
1. Im Railway Dashboard: **"Add Service"** → **"Database"** → **"PostgreSQL"**
2. Railway setzt automatisch die `DATABASE_URL` Environment Variable

### Schritt 4: Discord Bot Token setzen

#### Option A: Railway CLI (Empfohlen)
```bash
# Railway CLI installieren
npm install -g @railway/cli

# Login und Projekt verknüpfen
railway login
railway link

# Discord Bot Token setzen
railway variables set DISCORD_BOT_TOKEN="YOUR_DISCORD_BOT_TOKEN_HERE"
```

#### Option B: Railway Web Interface
1. Gehe zu deinem Railway Projekt
2. **"Variables"** Tab
3. Füge hinzu: `DISCORD_BOT_TOKEN` = `YOUR_DISCORD_BOT_TOKEN_HERE`

### Schritt 5: Deployment überwachen
- Railway deployed automatisch bei jedem Git Push
- Logs sind im Railway Dashboard verfügbar
- Nutze `/status` Command im Discord für Health Checks

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

## 📋 Verfügbare Befehle

### 🏓 General Commands
- `/ping` - Zeigt Bot-Latenz und Uptime
- `/status` - Detaillierte Bot-Status-Informationen für Monitoring
- `/help` - Hilfe und Bot-Informationen

### 🔧 Monitoring Features
- Health Check über `/status` Command
- Strukturierte Logs für Railway
- Automatische Reconnection bei Datenbankfehlern
- Graceful Shutdown für Railway Deployments

## 🏗️ Entwicklung

### Lokale Entwicklung
```bash
# Virtual Environment aktivieren
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

# Bot lokal starten
python bot.py
```

### Neue Cogs hinzufügen
1. Erstelle eine neue `.py` Datei in `cogs/`
2. Implementiere die Cog-Klasse
3. Füge die `setup()` Funktion hinzu
4. Der Bot lädt automatisch alle Cogs beim Start

### Datenbank erweitern
Erweitere die `init_db()` Funktion in `database.py` um neue Tabellen oder Spalten.

## 🚨 Railway-spezifische Features

- **Automatische DATABASE_URL Erkennung**
- **Retry-Logik für Datenbankverbindungen**
- **Signal Handler für graceful shutdown**
- **Optimierte Logging für Railway Monitoring**
- **Connection Pooling für bessere Performance**
