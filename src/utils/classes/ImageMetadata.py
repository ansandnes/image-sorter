# Standard Library Imports
from datetime import datetime
from pathlib import Path

# Module Imports
from src.utils.classes.GPSCoordinates import GPSCoordinates
from src.utils.classes.Location import Location


class ImageMetadata:
    """
    Everything the sorter knows about one photo or video file.
    Any of taken_at, gps and location may be None when the file lacks that information.
    """

    def __init__(
        self,
        path: Path,
        taken_at: datetime | None = None,
        gps: GPSCoordinates | None = None,
        location: Location | None = None,
    ):
        self.path: Path = path
        self.taken_at: datetime | None = taken_at
        self.gps: GPSCoordinates | None = gps
        self.location: Location | None = location

    def set_gps(self, gps: GPSCoordinates | None):
        self.gps = gps
        return self.gps

    def set_location(self, location: Location | None):
        self.location = location
        return self.location

    def set_taken_at(self, taken_at: datetime | None):
        self.taken_at = taken_at
        return self.taken_at

    def get_path(self) -> Path:
        return self.path

    def get_name(self) -> str:
        return self.path.name

    def get_taken_at(self) -> datetime | None:
        return self.taken_at

    def get_gps(self) -> GPSCoordinates | None:
        return self.gps

    def get_location(self) -> Location | None:
        return self.location

    def is_complete(self) -> bool:
        """True when both a capture date and a location are known."""
        return self.taken_at is not None and self.location is not None
