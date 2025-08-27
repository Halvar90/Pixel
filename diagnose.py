# Optional: diagnose.py für Pixel Bot
# Einfache Diagnose-Endpunkte für Railway Monitoring

import asyncio
from datetime import datetime, timezone
from lifecycle import get_recent_events, log_system_event

async def get_bot_health():
    """Gibt den aktuellen Bot-Status zurück."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0",
        "environment": "railway"
    }

async def get_recent_logs(limit: int = 50):
    """Gibt die letzten Log-Events zurück."""
    log_system_event("Diagnose API accessed", f"Requested {limit} recent logs")
    return {
        "events": get_recent_events(limit),
        "count": len(get_recent_events(limit)),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# Diese Datei kann später für eine FastAPI-Integration verwendet werden
# um Railway Monitoring-Dashboards zu erstellen
