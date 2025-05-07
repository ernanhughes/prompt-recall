from prompt_recall.db import connect
from datetime import datetime
import ollama


def call_model(prompt: str, model_name: str) -> str:
    response = ollama.chat(
        model=model_name,
        messages=[{"role": "user", "content": prompt}]
    )
    return response["message"]["content"].strip()


def generate_alternates(model_name: str = "llama3"):
    with connect() as conn:
        with conn.cursor() as cur:
            # Get all user messages
            cur.execute("""
                SELECT id, session_id, turn_index, content
                FROM chat_turns
                WHERE role = 'user'
                ORDER BY session_id, turn_index
            """)
            user_turns = cur.fetchall()

            for turn_id, session_id, turn_index, user_content in user_turns:
                # Skip if already generated
                cur.execute("SELECT 1 FROM alt_completions WHERE turn_id = %s AND model_name = %s",
                            (turn_id, model_name))
                if cur.fetchone():
                    continue

                prompt = user_content.strip()
                try:
                    response = call_model(prompt, model_name)
                except Exception as e:
                    print(f"[AltGen] Error from model {model_name} on turn {turn_id}: {e}")
                    continue

                cur.execute("""
                    INSERT INTO alt_completions (turn_id, model_name, alt_response, generated_at)
                    VALUES (%s, %s, %s, %s)
                """, (turn_id, model_name, response, datetime.utcnow()))

            conn.commit()
Go ahead send the money