# src/game/event_manager.py
import random
from typing import List, Dict, Any, Optional
from .player_manager import Player

class BaseEvent:
    """Basisklasse für alle Erkundungs-Events."""
    def __init__(self, event_data: Dict[str, Any]):
        self.id: str = event_data.get('id', 'unknown_event')
        self.display_text: str = event_data.get('display_text', 'Ein Event ist aufgetreten.')
        self.options: List[Dict[str, Any]] = event_data.get('options', [])

    def is_available(self, player: Player) -> bool:
        """Prüft, ob dieses Event für den Spieler verfügbar ist."""
        # Intelligenter Filter wird hier später implementiert
        return True

async def get_random_event(player: Player) -> Optional[BaseEvent]:
    """Lädt, filtert und wählt ein zufälliges, passendes Event für den Spieler aus."""
    # Platzhalter: Später werden diese Daten aus den `data/` JSON-Dateien geladen
    mock_events_data = [
        {
            "id": "common_stream",
            "display_text": "Du erreichst einen klaren, plätschernden Bach. Das Wasser sieht erfrischend aus.",
            "options": [
                {"label": "💧 Wasser schöpfen", "action": "collect_water", "reward": {"item": "reines_wasser", "quantity": 3}},
                {"label": "🧘 Kurz ausruhen", "action": "rest", "reward": {"buff": "mana_regen_boost_5pct_1h"}},
            ]
        },
        {
            "id": "common_berries",
            "display_text": "Du findest ein dichtes Dickicht voller saftiger Beeren.",
            "options": [
                {"label": "🧺 Vorsichtig pflücken", "action": "collect_berries_safe", "reward": {"item": "normale_beere", "quantity": 3}},
                {"label": "🌿 Tiefer hineingehen", "action": "collect_berries_risk", "reward": {"item": "normale_beere", "quantity": 5}, "consequence": "seelentier_kratzer"},
            ]
        }
    ]
    
    all_events = [BaseEvent(data) for data in mock_events_data]
    
    # Intelligenter Filter anwenden
    available_events = [event for event in all_events if event.is_available(player)]
    
    if not available_events:
        return None
        
    return random.choice(available_events)
