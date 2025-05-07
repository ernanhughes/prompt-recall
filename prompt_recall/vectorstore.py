# Vector embedding and search
import numpy as np
import psycopg
from typing import List
from prompt_recall.db import connect

# Dummy embedding generator — replace with real embedding model (e.g., Ollama)
def get_embedding(text: str) -> List[float]:
    # Return a placeholder vector — use your embedding model here
    return np.random.rand(1536).tolist()

def embed_and_store(turns: List[dict]):
    from prompt_recall.db import connect
    with connect() as conn:
        with conn.cursor() as cur:
            for turn in turns:
                for role in ["user", "assistant"]:
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

def query_similar(text: str, limit: int = 10):
    query_vec = get_embedding(text)
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT session_id, turn_index, role, content,
                1 - (embedding <=> %s) AS score
                FROM chat_turns
                ORDER BY embedding <=> %s
                LIMIT %s
            """, (query_vec, query_vec, limit))
            return cur.fetchall()
