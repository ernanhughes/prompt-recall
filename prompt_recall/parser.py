# Markdown parser module
import re
import time

def parse_markdown_chat(filepath: str, session_id: str = None) -> list[dict]:
    time.sleep(2)
    text = ""
    for attempt in range(3):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
                print(f"[Parser] Read {len(text)} characters from {filepath}")
            break
        except PermissionError as e:
            if attempt < 2:
                time.sleep(2)
            else:
                raise e

    pattern = re.compile(r"\*\*(You|ChatGPT):\*\*\s*\n(.*?)\n(?=\*\*|$)", re.DOTALL)
    matches = pattern.findall(text)

    turns = []
    turn_index = 0
    session = session_id or filepath.split("/")[-1].replace(".md", "")

    pair = {}
    for speaker, content in matches:
        speaker = speaker.strip().lower()
        if speaker == "you":
            pair["user"] = content.strip()
        elif speaker == "chatgpt":
            pair["assistant"] = content.strip()

        if "user" in pair and "assistant" in pair:
            turns.append({
                "session_id": session,
                "turn_index": turn_index,
                "user": pair["user"],
                "assistant": pair["assistant"]
            })
            turn_index += 1
            pair = {}

    return turns
