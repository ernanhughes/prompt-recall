import argparse
from prompt_recall.db import init_db
from prompt_recall.watcher import start_watching

def main():
    parser = argparse.ArgumentParser(description="PromptRecall CLI")
    parser.add_argument("--init-db", action="store_true", help="Initialize the database schema")
    parser.add_argument("--watch", action="store_true", help="Start watching the downloads folder for new chats")

    args = parser.parse_args()

    if args.init_db:
        print("[CLI] Initializing the database...")
        init_db()
        print("[CLI] Database initialized.")

    if args.watch:
        print("[CLI] Starting file watcher...")
        start_watching()

if __name__ == "__main__":
    main()
