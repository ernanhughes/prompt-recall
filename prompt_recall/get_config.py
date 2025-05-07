from prompt_recall.config import settings
from prompt_recall.db import connect

def get_config(key: str) -> str:
    try:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT value FROM app_config WHERE key = %s", (key,))
                row = cur.fetchone()
                if row:
                    return row[0]
    except Exception as e:
        print(f"[Config] Warning: DB config lookup failed for '{key}': {e}")
    return getattr(settings, key, None)
