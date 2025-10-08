# Standard Library Imports
from pathlib import Path

class ImagePath:
    def __init__(self, path: str):
        self._path = Path(path)

    def is_valid(self) -> bool:
        """Check if the path exists and is a directory."""
        return self._path.is_dir()

    def get_path(self) -> str:
        """Return string path."""
        return str(self._path)