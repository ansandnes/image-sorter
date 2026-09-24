import shutil
import tempfile
import unittest
from pathlib import Path

from src.core.processing_state import (
    compute_file_hash,
    get_recorded_destination,
    initialize_processing_state,
    is_hash_processed,
    record_processed_image,
)


class TestProcessingState(unittest.TestCase):
    def test_records_and_detects_processed_hash(self) -> None:
        temp_dir = tempfile.mkdtemp()
        try:
            image_dir = Path(temp_dir)
            file_path = image_dir / "sample.jpg"
            file_path.write_bytes(b"sample-content")

            db_path = initialize_processing_state(image_dir / "state" / "state.db")
            file_hash = compute_file_hash(str(file_path))

            self.assertFalse(is_hash_processed(db_path, file_hash))

            record_processed_image(
                db_path=db_path,
                file_hash=file_hash,
                original_path="Unsorted/sample.jpg",
                destination_path="Sorted/2024/Norway/Oslo/sample.jpg",
            )
            self.assertTrue(is_hash_processed(db_path, file_hash))

            # Recording the same hash again updates the destination.
            record_processed_image(
                db_path=db_path,
                file_hash=file_hash,
                original_path="Unsorted/sample.jpg",
                destination_path="Sorted/_Unknown/sample.jpg",
            )
            self.assertEqual(get_recorded_destination(db_path, file_hash), "Sorted/_Unknown/sample.jpg")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
