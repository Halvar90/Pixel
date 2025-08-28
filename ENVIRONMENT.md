# Environment Setup für Pixel Bot

## 🔧 Lokale Entwicklung

1. **`.env` Datei erstellen:**
   ```bash
   cp .env.example .env
   ```

2. **Discord Token eintragen:**
   - Gehe zu https://discord.com/developers/applications
   - Erstelle eine neue Application oder wähle eine bestehende
   - Unter "Bot" → "Token" → "Copy"
   - Füge den Token in die `.env` Datei ein:
     ```
     DISCORD_TOKEN=dein_echter_discord_token_hier
     MAIN_GUILD_ID=deine_server_id_hier
     ```

## 🚀 Railway Deployment

Railway nutzt Umgebungsvariablen für die Konfiguration:

### **Required Variables:**
- `DISCORD_TOKEN` - Dein Discord Bot Token
- `MAIN_GUILD_ID` - Discord Server ID für Emojis

### **Auto-Generated (Railway):**
- `DATABASE_URL` - PostgreSQL Verbindung
- `REDIS_URL` - Redis Verbindung

### **Setup auf Railway:**
1. Gehe zu deinem Railway Projekt
2. Klicke auf "Variables" 
3. Füge hinzu:
   ```
   DISCORD_TOKEN = dein_discord_token
   MAIN_GUILD_ID = deine_server_id
   ```

## 🛡️ Sicherheit

- **Niemals** Discord Tokens in den Code schreiben
- **Niemals** `.env` Dateien committen
- Tokens nur über Umgebungsvariablen verwenden
- `.env.example` als Template für andere Entwickler

## 📝 Environment Variables

| Variable | Beschreibung | Beispiel |
|----------|--------------|----------|
| `DISCORD_TOKEN` | Discord Bot Token | `MTIzNDU2Nzg5...` |
| `MAIN_GUILD_ID` | Discord Server ID | `123456789012345678` |
| `DATABASE_URL` | PostgreSQL Verbindung | `postgresql://...` |
| `REDIS_URL` | Redis Verbindung | `redis://...` |
| `ENVIRONMENT` | Umgebung (development/production) | `production` |
