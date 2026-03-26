from sqlalchemy import create_engine, text, inspect
import pandas as pd

DB_PATH = "./db/database.db"
_engine = None

def get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
    return _engine

def get_schema() -> str:
    inspector = inspect(get_engine())
    parts = []
    for table in inspector.get_table_names():
        cols = inspector.get_columns(table)
        col_str = ", ".join(f"{c['name']} {c['type']}" for c in cols)
        parts.append(f"TABLE {table} ({col_str})")
    return "\n".join(parts) if parts else "Δεν υπάρχουν tables ακόμα."

def ingest_csv(file_path: str, table_name: str) -> int:
    df = pd.read_csv(file_path)
    df.to_sql(table_name, get_engine(), if_exists="replace", index=False)
    return len(df)

def execute_select(sql: str) -> dict:
    if not sql.strip().upper().startswith("SELECT"):
        raise ValueError("Επιτρέπονται μόνο SELECT ερωτήματα.")
    with get_engine().connect() as conn:
        result = conn.execute(text(sql))
        rows = [list(r) for r in result.fetchall()]
        columns = list(result.keys())
    return {"columns": columns, "rows": rows, "count": len(rows)}

def execute_crud(sql: str) -> str:
    with get_engine().connect() as conn:
        conn.execute(text(sql))
        conn.commit()
    return "Η εντολή εκτελέστηκε επιτυχώς."