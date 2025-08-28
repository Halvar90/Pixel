"""
Intelligentes Discord Command Registration System
Automatische Erkennung und Sync von Slash Commands mit Change Detection
"""

import os
import json
import hashlib
import logging
import asyncio
from typing import Dict, List, Optional, Set, Any
from pathlib import Path
from datetime import datetime

import discord
from discord.ext import commands
from discord.app_commands import CommandTree

logger = logging.getLogger(__name__)

class CommandRegistrationSystem:
    """Intelligentes Command Registration System für Discord.py"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.tree = bot.tree
        
        # Command State Files
        self.state_dir = Path("data/command_state")
        self.state_dir.mkdir(parents=True, exist_ok=True)
        
        self.commands_hash_file = self.state_dir / "commands_hash.json"
        self.sync_log_file = self.state_dir / "sync_log.json"
        self.global_commands_file = self.state_dir / "global_commands.json"
        
        # Command Change Detection
        self.last_commands_hash = self._load_commands_hash()
        self.sync_history = self._load_sync_log()
        
        # Sync Status
        self.is_syncing = False
        self.last_sync_time = None
        self.sync_cooldown = 60  # Sekunden zwischen Syncs (Discord Rate Limit)
        
    def _load_commands_hash(self) -> str:
        """Lädt gespeicherten Commands Hash"""
        try:
            if self.commands_hash_file.exists():
                data = json.loads(self.commands_hash_file.read_text())
                return data.get("hash", "")
            return ""
        except Exception as e:
            logger.error(f"Fehler beim Laden des Commands Hash: {e}")
            return ""
    
    def _save_commands_hash(self, hash_value: str, commands_data: Dict[str, Any]):
        """Speichert Commands Hash mit Metadaten"""
        try:
            data = {
                "hash": hash_value,
                "timestamp": datetime.now().isoformat(),
                "command_count": len(commands_data.get("commands", [])),
                "global_commands": commands_data.get("global_commands", []),
                "cog_commands": commands_data.get("cog_commands", {})
            }
            self.commands_hash_file.write_text(json.dumps(data, indent=2))
        except Exception as e:
            logger.error(f"Fehler beim Speichern des Commands Hash: {e}")
    
    def _load_sync_log(self) -> List[Dict[str, Any]]:
        """Lädt Sync-Historie"""
        try:
            if self.sync_log_file.exists():
                return json.loads(self.sync_log_file.read_text())
            return []
        except Exception as e:
            logger.error(f"Fehler beim Laden der Sync-Historie: {e}")
            return []
    
    def _save_sync_log_entry(self, sync_data: Dict[str, Any]):
        """Speichert Sync-Log-Eintrag"""
        try:
            self.sync_history.append(sync_data)
            
            # Nur die letzten 50 Einträge behalten
            if len(self.sync_history) > 50:
                self.sync_history = self.sync_history[-50:]
            
            self.sync_log_file.write_text(json.dumps(self.sync_history, indent=2))
        except Exception as e:
            logger.error(f"Fehler beim Speichern des Sync-Logs: {e}")
    
    def get_current_commands(self) -> Dict[str, Any]:
        """Extrahiert alle aktuellen Commands aus dem Bot"""
        commands_data = {
            "commands": [],
            "global_commands": [],
            "cog_commands": {}
        }
        
        try:
            # Global Commands vom CommandTree
            for command in self.tree._global_commands.values():
                if hasattr(command, 'name'):
                    cmd_data = {
                        "name": command.name,
                        "description": getattr(command, 'description', ''),
                        "type": type(command).__name__,
                        "options": self._extract_command_options(command)
                    }
                    commands_data["commands"].append(cmd_data)
                    commands_data["global_commands"].append(cmd_data)
            
            # Commands von Cogs
            for cog_name, cog in self.bot.cogs.items():
                cog_commands = []
                
                # App Commands aus Cogs
                if hasattr(cog, 'get_app_commands'):
                    for command in cog.get_app_commands():
                        cmd_data = {
                            "name": command.name,
                            "description": getattr(command, 'description', ''),
                            "type": type(command).__name__,
                            "cog": cog_name,
                            "options": self._extract_command_options(command)
                        }
                        commands_data["commands"].append(cmd_data)
                        cog_commands.append(cmd_data)
                
                # Walk through App Commands (für Groups etc.)
                if hasattr(cog, 'walk_app_commands'):
                    for command in cog.walk_app_commands():
                        cmd_data = {
                            "name": command.name,
                            "description": getattr(command, 'description', ''),
                            "type": type(command).__name__,
                            "cog": cog_name,
                            "qualified_name": getattr(command, 'qualified_name', command.name),
                            "options": self._extract_command_options(command)
                        }
                        
                        # Prüfen ob Command bereits hinzugefügt wurde
                        if not any(cmd["name"] == cmd_data["name"] and 
                                 cmd.get("qualified_name") == cmd_data.get("qualified_name")
                                 for cmd in commands_data["commands"]):
                            commands_data["commands"].append(cmd_data)
                            cog_commands.append(cmd_data)
                
                if cog_commands:
                    commands_data["cog_commands"][cog_name] = cog_commands
            
            return commands_data
            
        except Exception as e:
            logger.error(f"Fehler beim Extrahieren der Commands: {e}")
            return commands_data
    
    def _extract_command_options(self, command) -> List[Dict[str, Any]]:
        """Extrahiert Command Options/Parameter"""
        options = []
        
        try:
            if hasattr(command, 'parameters'):
                for param in command.parameters:
                    option_data = {
                        "name": param.name,
                        "type": str(param.type) if hasattr(param, 'type') else "unknown",
                        "required": getattr(param, 'required', False),
                        "description": getattr(param, 'description', '')
                    }
                    options.append(option_data)
            
            if hasattr(command, '_params'):
                for param_name, param in command._params.items():
                    option_data = {
                        "name": param_name,
                        "type": str(type(param)) if param else "unknown",
                        "annotation": str(getattr(param, 'annotation', ''))
                    }
                    options.append(option_data)
                    
        except Exception as e:
            logger.debug(f"Fehler beim Extrahieren der Command Options: {e}")
        
        return options
    
    def calculate_commands_hash(self, commands_data: Dict[str, Any]) -> str:
        """Berechnet Hash der aktuellen Commands"""
        try:
            # Commands für Hash normalisieren (sortieren für Konsistenz)
            normalized_commands = sorted(
                commands_data["commands"],
                key=lambda x: (x.get("name", ""), x.get("qualified_name", ""))
            )
            
            # Hash-relevante Daten extrahieren
            hash_data = {
                "commands": normalized_commands,
                "command_count": len(normalized_commands)
            }
            
            # Hash berechnen
            commands_str = json.dumps(hash_data, sort_keys=True)
            return hashlib.sha256(commands_str.encode()).hexdigest()
            
        except Exception as e:
            logger.error(f"Fehler bei Commands-Hash-Berechnung: {e}")
            return ""
    
    def detect_command_changes(self) -> Dict[str, Any]:
        """Erkennt Änderungen an Commands"""
        try:
            current_commands = self.get_current_commands()
            current_hash = self.calculate_commands_hash(current_commands)
            
            changes_detected = current_hash != self.last_commands_hash
            
            change_info = {
                "changes_detected": changes_detected,
                "current_hash": current_hash,
                "previous_hash": self.last_commands_hash,
                "command_count": len(current_commands["commands"]),
                "global_commands": len(current_commands["global_commands"]),
                "cog_commands": {cog: len(cmds) for cog, cmds in current_commands["cog_commands"].items()},
                "timestamp": datetime.now().isoformat()
            }
            
            if changes_detected:
                logger.info(f"Command-Änderungen erkannt: {len(current_commands['commands'])} Commands")
                
                # Detaillierte Änderungen ermitteln
                change_info["details"] = self._analyze_command_changes(current_commands)
            else:
                logger.debug("Keine Command-Änderungen erkannt")
            
            return change_info
            
        except Exception as e:
            logger.error(f"Fehler bei Command-Change-Detection: {e}")
            return {
                "changes_detected": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _analyze_command_changes(self, current_commands: Dict[str, Any]) -> Dict[str, List[str]]:
        """Analysiert detaillierte Command-Änderungen"""
        details = {
            "added": [],
            "removed": [],
            "modified": []
        }
        
        try:
            # Lade vorherige Commands
            if self.global_commands_file.exists():
                previous_commands = json.loads(self.global_commands_file.read_text())
            else:
                previous_commands = {"commands": []}
            
            # Command Namen für Vergleich
            current_names = {cmd["name"] for cmd in current_commands["commands"]}
            previous_names = {cmd["name"] for cmd in previous_commands["commands"]}
            
            # Hinzugefügte Commands
            details["added"] = list(current_names - previous_names)
            
            # Entfernte Commands
            details["removed"] = list(previous_names - current_names)
            
            # Geänderte Commands (Namen vorhanden, aber Hash anders)
            common_names = current_names & previous_names
            for name in common_names:
                current_cmd = next(cmd for cmd in current_commands["commands"] if cmd["name"] == name)
                previous_cmd = next(cmd for cmd in previous_commands["commands"] if cmd["name"] == name)
                
                current_cmd_hash = hashlib.sha256(json.dumps(current_cmd, sort_keys=True).encode()).hexdigest()
                previous_cmd_hash = hashlib.sha256(json.dumps(previous_cmd, sort_keys=True).encode()).hexdigest()
                
                if current_cmd_hash != previous_cmd_hash:
                    details["modified"].append(name)
            
        except Exception as e:
            logger.error(f"Fehler bei detaillierter Change-Analyse: {e}")
        
        return details
    
    async def check_sync_needed(self) -> Dict[str, Any]:
        """Prüft ob Command-Sync erforderlich ist"""
        change_info = self.detect_command_changes()
        
        sync_needed = change_info["changes_detected"]
        
        # Rate Limit Check
        if self.last_sync_time:
            time_since_sync = (datetime.now() - self.last_sync_time).total_seconds()
            if time_since_sync < self.sync_cooldown:
                cooldown_remaining = self.sync_cooldown - time_since_sync
                sync_needed = False
                change_info["cooldown_remaining"] = cooldown_remaining
                change_info["sync_blocked"] = "Rate limit cooldown active"
        
        change_info["sync_needed"] = sync_needed
        return change_info
    
    async def intelligent_sync(self, force: bool = False, guild: Optional[discord.Guild] = None) -> Dict[str, Any]:
        """Intelligenter Command-Sync mit Change Detection"""
        sync_result = {
            "success": False,
            "message": "Sync nicht ausgeführt",
            "changes_detected": False,
            "commands_synced": 0,
            "sync_type": "none",
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # Sync Status prüfen
            if self.is_syncing and not force:
                sync_result["message"] = "Sync bereits in Bearbeitung"
                return sync_result
            
            # Change Detection
            sync_check = await self.check_sync_needed()
            sync_result["changes_detected"] = sync_check["changes_detected"]
            
            if not sync_check["sync_needed"] and not force:
                sync_result["message"] = sync_check.get("sync_blocked", "Keine Änderungen erkannt")
                return sync_result
            
            self.is_syncing = True
            
            try:
                # Commands vor Sync erfassen
                current_commands = self.get_current_commands()
                
                # Sync ausführen
                if guild:
                    # Guild-spezifischer Sync
                    synced_commands = await self.tree.sync(guild=guild)
                    sync_result["sync_type"] = f"guild_{guild.id}"
                    sync_result["guild"] = {"id": guild.id, "name": guild.name}
                else:
                    # Globaler Sync
                    synced_commands = await self.tree.sync()
                    sync_result["sync_type"] = "global"
                
                # Sync erfolgreich
                sync_result["success"] = True
                sync_result["commands_synced"] = len(synced_commands)
                sync_result["message"] = f"Successfully synced {len(synced_commands)} commands"
                
                # State aktualisieren
                current_hash = self.calculate_commands_hash(current_commands)
                self._save_commands_hash(current_hash, current_commands)
                self.last_commands_hash = current_hash
                self.last_sync_time = datetime.now()
                
                # Commands für Change Detection speichern
                self.global_commands_file.write_text(json.dumps(current_commands, indent=2))
                
                # Sync-Log speichern
                log_entry = {
                    "timestamp": sync_result["timestamp"],
                    "sync_type": sync_result["sync_type"],
                    "commands_synced": sync_result["commands_synced"],
                    "success": True,
                    "changes": sync_check.get("details", {}),
                    "hash": current_hash
                }
                
                if guild:
                    log_entry["guild_id"] = guild.id
                    log_entry["guild_name"] = guild.name
                
                self._save_sync_log_entry(log_entry)
                
                logger.info(f"Commands erfolgreich synchronisiert: {len(synced_commands)} commands ({sync_result['sync_type']})")
                
            except discord.HTTPException as e:
                sync_result["message"] = f"Discord API Fehler: {e}"
                sync_result["error_code"] = getattr(e, 'code', None)
                logger.error(f"Discord API Fehler beim Command-Sync: {e}")
                
                # Fehler-Log speichern
                self._save_sync_log_entry({
                    "timestamp": sync_result["timestamp"],
                    "sync_type": sync_result["sync_type"],
                    "success": False,
                    "error": str(e),
                    "error_code": getattr(e, 'code', None)
                })
                
            except Exception as e:
                sync_result["message"] = f"Unerwarteter Fehler: {e}"
                logger.error(f"Unerwarteter Fehler beim Command-Sync: {e}")
                
                # Fehler-Log speichern
                self._save_sync_log_entry({
                    "timestamp": sync_result["timestamp"],
                    "sync_type": sync_result["sync_type"],
                    "success": False,
                    "error": str(e)
                })
            
        finally:
            self.is_syncing = False
        
        return sync_result
    
    async def auto_sync_on_ready(self) -> Dict[str, Any]:
        """Automatischer Sync beim Bot-Start (wenn nötig)"""
        try:
            # Kurz warten damit alle Cogs geladen sind
            await asyncio.sleep(2)
            
            # Sync-Check
            sync_result = await self.intelligent_sync()
            
            if sync_result["success"]:
                logger.info("Auto-Sync beim Bot-Start erfolgreich")
            elif sync_result["changes_detected"]:
                logger.warning(f"Auto-Sync Fehler: {sync_result['message']}")
            else:
                logger.info("Auto-Sync: Keine Änderungen erkannt")
            
            return sync_result
            
        except Exception as e:
            logger.error(f"Fehler beim Auto-Sync: {e}")
            return {
                "success": False,
                "message": f"Auto-Sync Fehler: {e}",
                "timestamp": datetime.now().isoformat()
            }
    
    def get_sync_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Gibt Sync-Historie zurück"""
        return self.sync_history[-limit:] if self.sync_history else []
    
    def get_command_statistics(self) -> Dict[str, Any]:
        """Gibt Command-Statistiken zurück"""
        try:
            current_commands = self.get_current_commands()
            
            # Statistiken berechnen
            stats = {
                "total_commands": len(current_commands["commands"]),
                "global_commands": len(current_commands["global_commands"]),
                "cog_commands": len(current_commands["commands"]) - len(current_commands["global_commands"]),
                "cogs_with_commands": len(current_commands["cog_commands"]),
                "commands_by_cog": {
                    cog: len(cmds) for cog, cmds in current_commands["cog_commands"].items()
                },
                "last_sync": self.last_sync_time.isoformat() if self.last_sync_time else None,
                "total_syncs": len(self.sync_history),
                "successful_syncs": len([s for s in self.sync_history if s.get("success")]),
                "last_hash": self.last_commands_hash
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Fehler bei Command-Statistiken: {e}")
            return {"error": str(e)}
    
    async def force_sync_all(self, guild_ids: Optional[List[int]] = None) -> Dict[str, Any]:
        """Force-Sync für spezifische Guilds oder global"""
        results = {
            "global": None,
            "guilds": {},
            "summary": {
                "total_syncs": 0,
                "successful_syncs": 0,
                "failed_syncs": 0
            }
        }
        
        try:
            # Globaler Sync
            global_result = await self.intelligent_sync(force=True)
            results["global"] = global_result
            results["summary"]["total_syncs"] += 1
            
            if global_result["success"]:
                results["summary"]["successful_syncs"] += 1
            else:
                results["summary"]["failed_syncs"] += 1
            
            # Guild-spezifische Syncs
            if guild_ids:
                for guild_id in guild_ids:
                    guild = self.bot.get_guild(guild_id)
                    if guild:
                        guild_result = await self.intelligent_sync(force=True, guild=guild)
                        results["guilds"][guild_id] = guild_result
                        results["summary"]["total_syncs"] += 1
                        
                        if guild_result["success"]:
                            results["summary"]["successful_syncs"] += 1
                        else:
                            results["summary"]["failed_syncs"] += 1
                    else:
                        results["guilds"][guild_id] = {
                            "success": False,
                            "message": f"Guild {guild_id} nicht gefunden"
                        }
                        results["summary"]["total_syncs"] += 1
                        results["summary"]["failed_syncs"] += 1
            
        except Exception as e:
            logger.error(f"Fehler beim Force-Sync: {e}")
            results["error"] = str(e)
        
        return results

# Convenience Functions
def setup_command_registration(bot: commands.Bot) -> CommandRegistrationSystem:
    """Setup Command Registration System"""
    return CommandRegistrationSystem(bot)

async def auto_sync_commands(bot: commands.Bot) -> Dict[str, Any]:
    """Automatischer Command-Sync für Bot-Setup"""
    import asyncio
    
    try:
        cmd_system = setup_command_registration(bot)
        return await cmd_system.auto_sync_on_ready()
    except Exception as e:
        logger.error(f"Fehler beim Auto-Command-Sync: {e}")
        return {
            "success": False,
            "message": f"Command-Sync-Fehler: {str(e)}"
        }
