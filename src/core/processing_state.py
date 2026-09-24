import hashlib
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


def initialize_processing_state(db_path: Path | str) -> str:
    """
    Ensure state database exists and has required schema.
    """
    db_path = Path(db_path)
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
    return get_recorded_destination(db_path, file_hash) is not None


def get_recorded_destination(db_path: str, file_hash: str) -> str | None:
    """
    Return where a file with this hash was sorted to (relative to the drive root), if anywhere.
    """
    with sqlite3.connect(db_path) as connection:
        cursor = connection.execute(
            "SELECT destination_path FROM processed_images WHERE file_hash = ? LIMIT 1",
            (file_hash,),
        )
        row = cursor.fetchone()
        return row[0] if row else None


def record_processed_image(
    db_path: str, file_hash: str, original_path: str, destination_path: str
) -> None:
    """
    Persist processed image state for idempotent reruns.
    Paths should be relative to the drive root. A file sorted again (because its
    earlier copy was removed from Sorted) replaces the old record.
    """
    processed_at = datetime.now(timezone.utc).isoformat()
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            """
            INSERT INTO processed_images (
                file_hash, original_path, destination_path, processed_at
            ) VALUES (?, ?, ?, ?)
            ON CONFLICT(file_hash) DO UPDATE SET
                original_path = excluded.original_path,
                destination_path = excluded.destination_path,
                processed_at = excluded.processed_at
            """,
            (file_hash, original_path, destination_path, processed_at),
        )
        connection.commit()
