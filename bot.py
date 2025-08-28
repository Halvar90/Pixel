#!/usr/bin/env python3
"""
Pixel Discord Bot - Railway Starter
Startet den Bot aus dem src/ Verzeichnis
"""

import sys
import os
from pathlib import Path

# Füge src/ zum Python Path hinzu
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Importiere und starte den Bot
if __name__ == "__main__":
    try:
        from src.bot import main
        import asyncio
        asyncio.run(main())
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 Stelle sicher, dass src/bot.py existiert und korrekt ist")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Startup Error: {e}")
        sys.exit(1)