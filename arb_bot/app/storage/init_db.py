from pathlib import Path

from app.storage.db import engine
from app.storage.sql_utils import split_sql_statements


async def ensure_schema() -> None:
    """Apply bootstrap SQL migration if objects are missing."""
    migration_path = Path(__file__).resolve().parent / "migrations" / "0001_init.sql"
    sql_script = migration_path.read_text(encoding="utf-8")
    statements = split_sql_statements(sql_script)

    async with engine.begin() as conn:
        for statement in statements:
            await conn.exec_driver_sql(statement)
