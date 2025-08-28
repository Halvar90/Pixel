# Railway Deployment Guide 🚄

## 🚀 Railway Setup für Pixel Bot

### ✅ **Bereits konfiguriert:**

#### **Services:**
- 🐘 **PostgreSQL**: `postgres.railway.internal:5432`
- 🔴 **Redis**: `redis.railway.internal:6379`
- 🤖 **Bot Service**: Pixel

#### **Umgebungsvariablen:**
```env
DATABASE_URL=postgresql://postgres:***@postgres.railway.internal:5432/railway
REDIS_URL=redis://default:***@redis.railway.internal:6379
DISCORD_TOKEN=your_discord_token_here
```

### 🔧 **Deployment-Befehle:**

#### **1. Bot deployen:**
```bash
# Projekt zu Railway pushen
railway login
railway link
railway up
```

#### **2. Logs überwachen:**
```bash
railway logs --follow
```

#### **3. Service neustarten:**
```bash
railway redeploy
```

### 📊 **Externe Verbindungen (für lokale Entwicklung):**

Wenn du lokal entwickeln möchtest, verwende diese URLs:

```env
# Für lokale Entwicklung (.env)
POSTGRES_URL=postgresql://postgres:***@yamanote.proxy.rlwy.net:35334/railway
REDIS_URL=redis://default:***@shuttle.proxy.rlwy.net:34330
DISCORD_TOKEN=your_discord_token_here
```

### 🛠️ **Railway-CLI Befehle:**

```bash
# Projekt-Status anzeigen
railway status

# Umgebungsvariablen anzeigen
railway variables

# Service-Logs anzeigen
railway logs

# Datenbank-Shell öffnen
railway connect postgres

# Redis-CLI öffnen  
railway connect redis

# Bot neustarten
railway restart

# Environment wechseln
railway environment

# Domain anzeigen
railway domain
```

### 🔍 **Debugging:**

#### **Logs checken:**
```bash
railway logs --tail 100
```

#### **Service-Status prüfen:**
```bash
railway ps
```

#### **Verbindung testen:**
```bash
# Lokal testen
python test_connection.py

# Auf Railway testen
railway run python test_connection.py
```

### ⚠️ **Wichtige Hinweise:**

1. **Interne URLs**: Die `.railway.internal` URLs funktionieren nur innerhalb des Railway-Netzwerks
2. **Externe URLs**: Die `.proxy.rlwy.net` URLs sind für externe Verbindungen (lokale Entwicklung)
3. **Ports**: Die Ports der externen URLs können sich ändern
4. **SSL**: Alle Verbindungen verwenden SSL/TLS

### 🎯 **Nächste Schritte:**

1. **Bot testen:**
   ```bash
   python test_connection.py
   ```

2. **Bot starten:**
   ```bash
   python bot.py
   ```

3. **Auf Railway deployen:**
   ```bash
   railway up
   ```

4. **Discord-Server einladen:**
   - Gehe zu Discord Developer Portal
   - Erstelle einen Invite-Link mit den erforderlichen Permissions
   - Lade den Bot zu deinem Server ein

### 🔐 **Permissions für Discord:**

Der Bot benötigt folgende Permissions:
- `Send Messages`
- `Use Slash Commands`
- `Embed Links`
- `Read Message History`
- `Add Reactions`

**Permission Integer**: `274877943872`

**Invite URL Format:**
```
https://discord.com/api/oauth2/authorize?client_id=1410207945257390131&permissions=274877943872&scope=bot%20applications.commands
```

---
**Railway Project**: `Pixel` | **Environment**: `production` 🚄
