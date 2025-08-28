# Pixel Discord Bot 🤖✨

Ein hochmoderner, asynchroner Discord-Bot mit PostgreSQL und Redis-Integration für eine optimale Performance und Skalierbarkeit.

## 📋 Features

- **🎁 Daily System**: Tägliche Belohnungen mit Streak-Bonus
- **💰 Pixel Economy**: Sammle und verwalte Pixels
- **🔮 Mana System**: Regenerierbare Mana mit Cooldowns
- **🏆 Leaderboard**: Rangliste der besten Spieler
- **📊 Statistiken**: Server- und Bot-Statistiken
- **🚀 Performance**: Redis-Caching für optimale Geschwindigkeit
- **📈 Skalierbar**: PostgreSQL für persistente Datenbank

## 🛠️ Installation

### Voraussetzungen

- Python 3.11+
- PostgreSQL-Datenbank
- Redis-Server
- Discord Bot Token

### 1. Repository klonen

```bash
git clone <your-repo-url>
cd pixel-bot
```

### 2. Virtuelle Umgebung erstellen

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

### 3. Abhängigkeiten installieren

```bash
pip install -r requirements.txt
```

### 4. Umgebungsvariablen konfigurieren

Erstelle eine `.env`-Datei im Projektverzeichnis:

```env
DISCORD_BOT_TOKEN="dein_bot_token_hier"
POSTGRES_URL="postgresql://user:password@host:port/database"
REDIS_URL="redis://default:password@host:port"
FDT_CHANNEL_ID="kanal_id_für_frage_des_tages"
LOG_CHANNEL_ID="kanal_id_für_logs"
```

### 5. Datenbank initialisieren

Das Schema wird automatisch beim ersten Start des Bots erstellt.

### 6. Bot starten

```bash
python bot.py
```

## 📁 Projektstruktur

```
pixel-bot/
├── bot.py              # Haupt-Bot-Datei
├── database.py         # PostgreSQL-Verbindung und -Funktionen
├── cache.py           # Redis-Verbindung und -Funktionen
├── schema.sql         # Datenbankschema
├── requirements.txt   # Python-Abhängigkeiten
├── .env              # Umgebungsvariablen (nicht in Git)
├── .gitignore        # Git-Ignore-Datei
├── Procfile          # Heroku-Deployment
├── runtime.txt       # Python-Version für Heroku
├── cogs/             # Bot-Befehle (modulare Erweiterungen)
│   ├── __init__.py
│   ├── general.py    # Allgemeine Befehle
│   └── player.py     # Spieler-bezogene Befehle
└── events/           # Event-Handler
    └── __init__.py
```

## 🎮 Befehle

### Spieler-Befehle

- `/daily` - Tägliche Belohnung abholen (22h Cooldown)
- `/balance` - Pixel-Kontostand und Mana anzeigen
- `/mana` - Mana regenerieren (10min Cooldown)
- `/leaderboard` - Top 10 Spieler nach Pixels

### Allgemeine Befehle

- `/help` - Hilfe-Menü mit allen Befehlen
- `/ping` - Bot-Latenz prüfen
- `/info` - Bot-Informationen und Statistiken
- `/stats` - Server-Statistiken

## 🔧 Technische Details

### Datenbank-Schema

- **players**: Spielerdaten (Mana, Pixels, etc.)
- **items**: Sammelbare Gegenstände
- **player_inventory**: Spieler-Inventar
- **daily_rewards**: Tägliche Belohnungen
- **bot_logs**: Event-Logging

### Redis-Nutzung

- **Cooldowns**: `/daily`, `/mana` Befehle
- **Session-Daten**: Temporäre Spielerdaten
- **Streaks**: Tägliche Belohnungsstreaks
- **Caching**: Performance-Optimierung

### Performance-Features

- **Connection Pooling**: Effiziente Datenbankverbindungen
- **Async/Await**: Vollständig asynchrone Architektur
- **Error Handling**: Robuste Fehlerbehandlung
- **Logging**: Ausführliche Event-Protokollierung

## 🚀 Deployment

### Heroku

1. Erstelle eine neue Heroku-App
2. Füge PostgreSQL und Redis Add-ons hinzu
3. Setze die Umgebungsvariablen
4. Deploye mit Git

### Docker (Optional)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "bot.py"]
```

## 🔒 Sicherheit

- Alle sensiblen Daten in Umgebungsvariablen
- SQL-Injection-Schutz durch parametrisierte Queries
- Rate-Limiting durch Redis-Cooldowns
- Input-Validierung bei allen Befehlen

## 🤝 Beitragen

1. Fork das Repository
2. Erstelle einen Feature-Branch (`git checkout -b feature/AmazingFeature`)
3. Committe deine Änderungen (`git commit -m 'Add some AmazingFeature'`)
4. Push zum Branch (`git push origin feature/AmazingFeature`)
5. Öffne eine Pull Request

## 📝 Lizenz

Dieses Projekt steht unter der MIT-Lizenz. Siehe [LICENSE](LICENSE) für Details.

## 🆘 Support

Bei Fragen oder Problemen:
1. Öffne ein Issue im Repository
2. Prüfe die Logs für Fehlermeldungen
3. Stelle sicher, dass alle Umgebungsvariablen korrekt gesetzt sind

---

**Entwickelt mit ❤️ für die Discord-Community**
