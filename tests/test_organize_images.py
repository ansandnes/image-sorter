import logging
import shutil
import tempfile
import unittest
from pathlib import Path

from src.core.organize_images import organize_images
from src.utils.classes.ImageGPS import ImageGPS
from src.utils.classes.ImageMetadata import ImageMetadata
from src.utils.classes.Location import Location


class TestOrganizeImages(unittest.TestCase):
    def _build_metadata(self, image_dir: str, filename: str, timestamp: str) -> ImageMetadata:
        metadata = ImageMetadata(
            dir=image_dir,
            name=filename,
            timestamp=timestamp,
            coords=ImageGPS(None, None, None, None),
        )
        metadata.set_location(Location("Norway", "Oslo"))
        return metadata

    def test_dry_run_returns_expected_destination_and_preserves_source(self) -> None:
        temp_dir = tempfile.mkdtemp()
        try:
            image_dir = Path(temp_dir)
            filename = "photo.jpg"
            source_path = image_dir / filename
            source_path.write_bytes(b"test-image")

            metadata = self._build_metadata(temp_dir, filename, "2024:07:15 09:30:00")
            destination_path = organize_images(
                image_dir=temp_dir,
                image_metadata=metadata,
                filename=filename,
                dry_run=True,
            )

            self.assertIsNotNone(destination_path)
            self.assertTrue(source_path.exists())
            self.assertTrue(
                str(destination_path).endswith(
                    str(Path("Norway") / "Oslo" / "2024" / "07" / "photo.jpg")
                )
            )
        finally:
            logger = logging.getLogger("main")
            for handler in logger.handlers:
                handler.close()
            logger.handlers.clear()
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
