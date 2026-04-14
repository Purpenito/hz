from pathlib import Path

from app.storage.db import engine


async def ensure_schema() -> None:
    """Apply bootstrap SQL migration if objects are missing."""
    migration_path = Path(__file__).resolve().parent / "migrations" / "0001_init.sql"
    sql_script = migration_path.read_text(encoding="utf-8")
    async with engine.begin() as conn:
        await conn.exec_driver_sql(sql_script)
