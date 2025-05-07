# Configuration loading
import os
from dataclasses import dataclass

@dataclass
class Settings:
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_name: str = os.getenv("DB_NAME", "prompt_recall")
    db_user: str = os.getenv("DB_USER", "user")
    db_password: str = os.getenv("DB_PASSWORD", "password")
    db_port: int = int(os.getenv("DB_PORT", "5432"))
    watch_dir: str = os.getenv("WATCH_DIR", "downloads")
    model_name: str = os.getenv("MODEL_NAME", "qwen3")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "openai/text-embedding-ada-002")

    @property
    def dsn(self):
        return f"host={self.db_host} dbname={self.db_name} user={self.db_user} password={self.db_password} port={self.db_port}"

settings = Settings()
