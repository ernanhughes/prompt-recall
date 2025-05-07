# Postgres DB models and functions
from dataclasses import dataclass
from datetime import datetime
from typing import Literal
import psycopg
import os

DB_CONFIG = {
    "host": "localhost",
    "dbname": "prompt_recall",
    "user": "prompt_recall",
    "password": "prompt_recall"
}

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "../schema.sql")

@dataclass
class ChatTurn:
    session_id: str
    turn_index: int
    role: Literal["user", "assistant"]
    content: str
    embedding: list[float]
    created_at: datetime = datetime.utcnow()

def connect():
    return psycopg.connect(**DB_CONFIG)

def init_db():
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(schema_sql)
        conn.commit()

def insert_chat_turns(turns: list[dict]):
    from prompt_recall.vectorstore import get_embedding

    with connect() as conn:
        with conn.cursor() as cur:
            for turn in turns:
                for role in ("user", "assistant"):
                    content = turn.get(role, "").strip()
                    if content:
                        embedding = get_embedding(content)
                        cur.execute("""
                            INSERT INTO chat_turns (session_id, turn_index, role, content, embedding)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (
                            turn["session_id"],
                            turn["turn_index"],
                            role,
                            content,
                            embedding
                        ))
        conn.commit()
