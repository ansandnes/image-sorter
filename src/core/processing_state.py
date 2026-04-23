import hashlib
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


def _db_path(image_dir: str) -> Path:
    return Path(image_dir) / ".image_sorter" / "state.db"


def initialize_processing_state(image_dir: str) -> str:
    """
    Ensure state database exists and has required schema.
    """
    db_path = _db_path(image_dir)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS processed_images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_hash TEXT NOT NULL UNIQUE,
                original_path TEXT NOT NULL,
                destination_path TEXT NOT NULL,
                processed_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_processed_images_file_hash
            ON processed_images(file_hash)
            """
        )
        connection.commit()

    return str(db_path)


def compute_file_hash(file_path: str, chunk_size: int = 1024 * 1024) -> str:
    """
    Compute SHA-256 hash for a file.
    """
    file_hash = hashlib.sha256()
    with open(file_path, "rb") as file_handle:
        while True:
            chunk = file_handle.read(chunk_size)
            if not chunk:
                break
            file_hash.update(chunk)
    return file_hash.hexdigest()


def is_hash_processed(db_path: str, file_hash: str) -> bool:
    """
    Return True when hash already exists in state database.
    """
    with sqlite3.connect(db_path) as connection:
        cursor = connection.execute(
            "SELECT 1 FROM processed_images WHERE file_hash = ? LIMIT 1",
            (file_hash,),
        )
        return cursor.fetchone() is not None


def record_processed_image(
    db_path: str, file_hash: str, original_path: str, destination_path: str
) -> None:
    """
    Persist processed image state for idempotent reruns.
    """
    processed_at = datetime.now(timezone.utc).isoformat()
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            """
            INSERT OR IGNORE INTO processed_images (
                file_hash, original_path, destination_path, processed_at
            ) VALUES (?, ?, ?, ?)
            """,
            (file_hash, original_path, destination_path, processed_at),
        )
        connection.commit()
