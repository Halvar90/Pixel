# src/game/item_manager.py
"""
Item-Management-System für den Pixel Bot
Platzhalter-Implementation für zukünftige Features
"""

from typing import Dict, List, Optional, Any
import json
import os
import logging

logger = logging.getLogger(__name__)

class Item:
    """Basis-Klasse für alle Items im Spiel."""
    
    def __init__(self, item_id: str, name: str, description: str, category: str = "misc"):
        self.id = item_id
        self.name = name
        self.description = description
        self.category = category
    
    def __repr__(self):
        return f"Item({self.id}: {self.name})"

class ItemManager:
    """Verwaltet alle Items und Item-Operationen."""
    
    def __init__(self):
        self.items: Dict[str, Item] = {}
        self._load_items()
    
    def _load_items(self):
        """Lädt Items aus der items.json Datei."""
        try:
            items_path = os.path.join("data", "items.json")
            if os.path.exists(items_path):
                with open(items_path, 'r', encoding='utf-8') as f:
                    items_data = json.load(f)
                
                for item_data in items_data.get('items', []):
                    item = Item(
                        item_id=item_data.get('id'),
                        name=item_data.get('name', 'Unbekanntes Item'),
                        description=item_data.get('description', 'Keine Beschreibung verfügbar.'),
                        category=item_data.get('category', 'misc')
                    )
                    self.items[item.id] = item
                
                logger.info(f"✅ {len(self.items)} Items geladen")
            else:
                logger.warning("⚠️ items.json nicht gefunden - leeres Item-System gestartet")
                
        except Exception as e:
            logger.error(f"❌ Fehler beim Laden der Items: {e}")
    
    def get_item(self, item_id: str) -> Optional[Item]:
        """Gibt ein Item anhand seiner ID zurück."""
        return self.items.get(item_id)
    
    def get_items_by_category(self, category: str) -> List[Item]:
        """Gibt alle Items einer bestimmten Kategorie zurück."""
        return [item for item in self.items.values() if item.category == category]

# Globale ItemManager-Instanz
item_manager = ItemManager()
