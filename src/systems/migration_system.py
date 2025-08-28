"""
Intelligentes Migration System für Discord Bot
Automatische Erkennung von Schema-Änderungen mit Alembic + PostgreSQL
"""

import os
import sys
import asyncio
import hashlib
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime

import asyncpg
from alembic import command, script
from alembic.config import Config
from alembic.runtime import migration
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.ext.asyncio import create_async_engine, async_engine_from_config
from sqlalchemy.pool import NullPool

logger = logging.getLogger(__name__)

class MigrationSystem:
    """Intelligentes Migration System mit Alembic für PostgreSQL auf Railway"""
    
    def __init__(self, database_url: str, alembic_config_path: str = "alembic.ini"):
        self.database_url = database_url
        self.async_database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
        self.alembic_config_path = alembic_config_path
        self.config = None
        self.script_directory = None
        
        # Schema Hash für Change Detection
        self.schema_hash_file = Path("data/schema_hash.txt")
        self.schema_hash_file.parent.mkdir(exist_ok=True)
        
    def setup_alembic_config(self):
        """Alembic Konfiguration initialisieren"""
        if not os.path.exists(self.alembic_config_path):
            self._create_alembic_config()
            
        self.config = Config(self.alembic_config_path)
        self.config.set_main_option("sqlalchemy.url", self.async_database_url)
        self.script_directory = ScriptDirectory.from_config(self.config)
        
    def _create_alembic_config(self):
        """Alembic Konfiguration erstellen wenn nicht vorhanden"""
        config_content = f"""# Alembic Configuration für Pixel Bot

[alembic]
# Template für async SQLAlchemy
script_location = migrations
prepend_sys_path = .
version_path_separator = os

# Async SQLAlchemy URL wird programmatisch gesetzt
sqlalchemy.url = {self.async_database_url}

[post_write_hooks]
# post_write_hooks definiert automatische Formatierung

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
"""
        
        with open(self.alembic_config_path, 'w') as f:
            f.write(config_content)
            
        # Migrations Directory erstellen
        migrations_dir = Path("migrations")
        migrations_dir.mkdir(exist_ok=True)
        
        # env.py für async SQLAlchemy erstellen
        env_py_content = '''"""Async SQLAlchemy Environment für Alembic"""
import asyncio
import os
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

# Alembic Config object für .ini file access
config = context.config

# Logging Setup
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target MetaData für Autogenerate Support
# Hier würden normalerweise die SQLAlchemy Models importiert werden
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = None

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations() -> None:
    """Run migrations in async mode."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = config.attributes.get("connection", None)

    if connectable is None:
        asyncio.run(run_async_migrations())
    else:
        do_run_migrations(connectable)

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
'''
        
        with open(migrations_dir / "env.py", 'w') as f:
            f.write(env_py_content)
            
        # script.py.mako Template
        template_content = '''"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
'''
        
        templates_dir = migrations_dir / "versions"
        templates_dir.mkdir(exist_ok=True)
        
        with open(migrations_dir / "script.py.mako", 'w') as f:
            f.write(template_content)
            
        logger.info("Alembic Konfiguration erstellt")

    async def initialize_database(self):
        """Datenbank initialisieren und Alembic Revision Table erstellen"""
        try:
            # Prüfen ob Alembic bereits initialisiert ist
            engine = create_async_engine(self.async_database_url, poolclass=NullPool)
            
            async with engine.connect() as conn:
                # Prüfen ob alembic_version Tabelle existiert
                result = await conn.execute(text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = 'alembic_version'
                    );
                """))
                
                table_exists = result.scalar()
                
                if not table_exists:
                    # Alembic Version Table erstellen
                    await conn.run_sync(self._sync_stamp_head)
                    await conn.commit()
                    logger.info("Alembic initialisiert - Datenbank bereit für Migrationen")
                else:
                    logger.info("Alembic bereits initialisiert")
                    
            await engine.dispose()
            
        except Exception as e:
            logger.error(f"Fehler bei Datenbank-Initialisierung: {e}")
            raise

    def _sync_stamp_head(self, connection):
        """Synchrone Hilfsfunktion für Alembic Stamp"""
        self.config.attributes['connection'] = connection
        command.stamp(self.config, "head")

    async def detect_schema_changes(self) -> bool:
        """Erkennt Schema-Änderungen durch Hash-Vergleich"""
        try:
            current_hash = await self._calculate_schema_hash()
            stored_hash = self._get_stored_schema_hash()
            
            if current_hash != stored_hash:
                logger.info(f"Schema-Änderungen erkannt: {stored_hash} -> {current_hash}")
                return True
            else:
                logger.debug("Keine Schema-Änderungen erkannt")
                return False
                
        except Exception as e:
            logger.error(f"Fehler bei Schema-Change-Detection: {e}")
            return False

    async def _calculate_schema_hash(self) -> str:
        """Berechnet Hash des aktuellen Schemas"""
        try:
            engine = create_async_engine(self.async_database_url, poolclass=NullPool)
            
            async with engine.connect() as conn:
                # Schema-Informationen abrufen
                schema_info = await conn.execute(text("""
                    SELECT 
                        table_name,
                        column_name,
                        data_type,
                        is_nullable,
                        column_default
                    FROM information_schema.columns 
                    WHERE table_schema = 'public'
                    ORDER BY table_name, ordinal_position;
                """))
                
                # Constraints abrufen
                constraints_info = await conn.execute(text("""
                    SELECT 
                        tc.table_name,
                        tc.constraint_name,
                        tc.constraint_type,
                        kcu.column_name
                    FROM information_schema.table_constraints tc
                    LEFT JOIN information_schema.key_column_usage kcu
                        ON tc.constraint_name = kcu.constraint_name
                    WHERE tc.table_schema = 'public'
                    ORDER BY tc.table_name, tc.constraint_name;
                """))
                
                # Alle Schema-Daten sammeln
                schema_data = {
                    'columns': [dict(row._mapping) for row in schema_info.fetchall()],
                    'constraints': [dict(row._mapping) for row in constraints_info.fetchall()]
                }
                
            await engine.dispose()
            
            # Hash berechnen
            schema_str = str(sorted(schema_data.items()))
            return hashlib.sha256(schema_str.encode()).hexdigest()
            
        except Exception as e:
            logger.error(f"Fehler bei Schema-Hash-Berechnung: {e}")
            return ""

    def _get_stored_schema_hash(self) -> str:
        """Lädt gespeicherten Schema-Hash"""
        try:
            if self.schema_hash_file.exists():
                return self.schema_hash_file.read_text().strip()
            return ""
        except Exception:
            return ""

    def _store_schema_hash(self, hash_value: str):
        """Speichert Schema-Hash"""
        try:
            self.schema_hash_file.write_text(hash_value)
        except Exception as e:
            logger.error(f"Fehler beim Speichern des Schema-Hash: {e}")

    def check_migration_status(self) -> Dict[str, Any]:
        """Prüft aktuellen Migration-Status"""
        try:
            engine = create_engine(self.database_url, poolclass=NullPool)
            
            with engine.connect() as connection:
                context = migration.MigrationContext.configure(connection)
                current_heads = context.get_current_heads()
                available_heads = self.script_directory.get_heads()
                
                is_up_to_date = set(current_heads) == set(available_heads)
                
                return {
                    'current_heads': list(current_heads),
                    'available_heads': list(available_heads),
                    'is_up_to_date': is_up_to_date,
                    'pending_migrations': len(available_heads) - len(current_heads)
                }
                
        except Exception as e:
            logger.error(f"Fehler bei Migration-Status-Check: {e}")
            return {'error': str(e)}

    async def create_migration(self, message: str = None) -> bool:
        """Erstellt neue Migration wenn Änderungen erkannt wurden"""
        try:
            if not await self.detect_schema_changes():
                logger.info("Keine Migrationen erforderlich")
                return False
            
            if not message:
                message = f"Auto-migration {datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Migration erstellen (sync Operation)
            command.revision(
                self.config,
                message=message,
                autogenerate=True
            )
            
            # Schema-Hash aktualisieren
            new_hash = await self._calculate_schema_hash()
            self._store_schema_hash(new_hash)
            
            logger.info(f"Migration erstellt: {message}")
            return True
            
        except Exception as e:
            logger.error(f"Fehler beim Erstellen der Migration: {e}")
            return False

    async def run_migrations(self) -> bool:
        """Führt ausstehende Migrationen aus"""
        try:
            engine = create_async_engine(self.async_database_url, poolclass=NullPool)
            
            async with engine.connect() as connection:
                # Alembic mit async Connection ausführen
                def run_upgrade(conn):
                    self.config.attributes['connection'] = conn
                    command.upgrade(self.config, "head")
                
                await connection.run_sync(run_upgrade)
                await connection.commit()
                
            await engine.dispose()
            
            # Schema-Hash nach Migration aktualisieren
            new_hash = await self._calculate_schema_hash()
            self._store_schema_hash(new_hash)
            
            logger.info("Migrationen erfolgreich ausgeführt")
            return True
            
        except Exception as e:
            logger.error(f"Fehler beim Ausführen der Migrationen: {e}")
            return False

    async def auto_migrate(self) -> Dict[str, Any]:
        """Automatischer Migrations-Prozess: Erkennung -> Erstellung -> Ausführung"""
        result = {
            'changes_detected': False,
            'migration_created': False,
            'migrations_applied': False,
            'status': 'success',
            'message': 'Keine Aktionen erforderlich'
        }
        
        try:
            # 1. Schema-Änderungen erkennen
            changes_detected = await self.detect_schema_changes()
            result['changes_detected'] = changes_detected
            
            if changes_detected:
                # 2. Migration erstellen
                migration_created = await self.create_migration("Auto-detected schema changes")
                result['migration_created'] = migration_created
                
                if migration_created:
                    # 3. Migrationen ausführen
                    migrations_applied = await self.run_migrations()
                    result['migrations_applied'] = migrations_applied
                    
                    if migrations_applied:
                        result['message'] = 'Schema-Änderungen erfolgreich migriert'
                    else:
                        result['status'] = 'error'
                        result['message'] = 'Fehler beim Ausführen der Migrationen'
                else:
                    result['status'] = 'error'
                    result['message'] = 'Fehler beim Erstellen der Migration'
            else:
                result['message'] = 'Schema ist aktuell - keine Migrationen erforderlich'
                
        except Exception as e:
            result['status'] = 'error'
            result['message'] = f'Unerwarteter Fehler: {str(e)}'
            logger.error(f"Fehler im Auto-Migration-Prozess: {e}")
            
        return result

    async def rollback_migration(self, target_revision: str = "-1") -> bool:
        """Führt Rollback zu spezifischer Revision durch"""
        try:
            engine = create_async_engine(self.async_database_url, poolclass=NullPool)
            
            async with engine.connect() as connection:
                def run_downgrade(conn):
                    self.config.attributes['connection'] = conn
                    command.downgrade(self.config, target_revision)
                
                await connection.run_sync(run_downgrade)
                await connection.commit()
                
            await engine.dispose()
            
            logger.info(f"Rollback zu Revision {target_revision} erfolgreich")
            return True
            
        except Exception as e:
            logger.error(f"Fehler beim Rollback: {e}")
            return False

# Convenience Functions
async def setup_migration_system(database_url: str) -> MigrationSystem:
    """Setup und Initialisierung des Migration Systems"""
    migration_system = MigrationSystem(database_url)
    migration_system.setup_alembic_config()
    await migration_system.initialize_database()
    return migration_system

async def auto_migrate_on_startup(database_url: str) -> Dict[str, Any]:
    """Führt automatische Migration beim Bot-Start aus"""
    try:
        migration_system = await setup_migration_system(database_url)
        return await migration_system.auto_migrate()
    except Exception as e:
        logger.error(f"Fehler beim Auto-Migration-Startup: {e}")
        return {
            'status': 'error',
            'message': f'Migration-System-Fehler: {str(e)}'
        }
