# Pixel - Simple Question of the Day Bot

Ein minimalistischer Discord Bot für automatische tägliche Fragen mit Thread-Diskussionen.

## 🎯 **Wie es funktioniert**

1. **Täglich um 9:00 Uhr** postet der Bot eine neue Frage im FdT-Channel
2. **Automatisch** wird ein Thread zur Frage erstellt
3. **Im Hauptchat** erscheint eine kurze Benachrichtigung mit Link zur Frage
4. **User klicken den Link**, sehen die Frage und können direkt im Thread antworten
5. **Keine Commands nötig** - alles läuft automatisch!

## 📋 **Features**

### **🤖 Vollautomatisch**
- **Tägliche Posts:** Jeden Tag um 9:00 Uhr eine neue Frage
- **Thread-Erstellung:** Automatischer Thread für Diskussionen  
- **Cross-Channel-Info:** Kurze Benachrichtigung im Hauptchat mit Link
- **400+ Fragen:** Umfangreicher Pool ohne Wiederholung

### **💬 Einfache Bedienung**
- **Für User:** Einfach auf Link klicken und im Thread antworten
- **Keine Commands:** User brauchen nichts zu tippen
- **Automatische Navigation:** Link führt direkt zur Frage + Thread

## 🔧 **Channel-Konfiguration**

- **FdT-Channel:** `1410229292230508595` (hier werden Fragen gepostet)
- **Hauptchat:** `1270678012341387268` (hier kommen die Benachrichtigungen)

## 🗃️ **Datenbank**

Verwendet PostgreSQL mit einer simplen Struktur:

```sql
CREATE TABLE fdt_questions (
    question_id SERIAL PRIMARY KEY,
    question_text TEXT NOT NULL,
    used_at TIMESTAMP NULL
);
```

## 🚀 **Deployment**

### **Railway Platform**
- PostgreSQL Database
- Automatisches Seeding mit 400+ Fragen
- 24/7 Verfügbarkeit mit Auto-Restart

### **Admin-Commands**
- `trigger_fdt` - Manueller Test-Trigger (nur für Admins)

## 📁 **Projektstruktur**

```
Pixel/
├── bot.py                 # Haupt-Bot
├── database.py            # PostgreSQL Verbindung
├── lifecycle.py          # Logging
├── seed_fdt.py           # 400+ Fragen für die Datenbank
├── cogs/
│   ├── minigames.py      # FdT-Automation
│   ├── admin.py          # Admin-Tools
│   └── general.py        # Basic Bot-Commands
└── README.md            # Diese Datei
```

## 🎮 **User Experience**

### **Täglicher Ablauf:**
1. **9:00 Uhr:** Bot postet Frage im FdT-Channel + Thread
2. **Hauptchat:** "📢 Neue Frage des Tages! [Link]"
3. **User:** Klickt Link → sieht Frage → antwortet im Thread
4. **Fertig!** Keine weiteren Schritte nötig

### **Automatische Features:**
- ✅ Thread wird automatisch erstellt
- ✅ Willkommensnachricht im Thread
- ✅ Reaktionen auf Frage-Post
- ✅ 24h Auto-Archive für Thread
- ✅ Kein Spam - nur 1 Benachrichtigung pro Tag

## 🔧 **Technisch**

- **Discord.py 2.6.2:** Moderne Discord API
- **PostgreSQL + asyncpg:** Async Datenbank
- **Railway Hosting:** Cloud-Deployment
- **Graceful Shutdown:** Sauberes Beenden

---

*Einfach, automatisch, effektiv - Question of the Day ohne Komplikationen! 🎯*
