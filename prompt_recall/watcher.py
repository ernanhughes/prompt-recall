import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from prompt_recall.parser import parse_chatgpt_markdown
from prompt_recall.db import insert_chat_turns
from prompt_recall.vectorstore import embed_and_store
from prompt_recall.get_config import get_config

WATCH_DIR = get_config("watch_dir")
if not os.path.exists(WATCH_DIR):
    os.makedirs(WATCH_DIR)

class MarkdownHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return

        if event.src_path.endswith(".md"):
            print(f"[Watcher] New markdown file detected: {event.src_path}")
            try:
                turns = parse_chatgpt_markdown(event.src_path)
                insert_chat_turns(turns)
                embed_and_store(turns)
                print(f"[Watcher] Successfully processed: {event.src_path}")
            except Exception as e:
                print(f"[Watcher] Error processing {event.src_path}: {e}")

def start_watching():
    print(f"[Watcher] Monitoring directory: {WATCH_DIR}")
    observer = Observer()
    event_handler = MarkdownHandler()
    observer.schedule(event_handler, WATCH_DIR, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    start_watching()
