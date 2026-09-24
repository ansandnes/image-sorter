# Standard Library imports
from pathlib import Path

# The repository folder (the one containing main.py).
REPO_DIR = Path(__file__).resolve().parents[2]


class AppPaths:
    """
    All folders the app uses, resolved from the drive root.

    Drive layout:
        <root>/Unsorted/            files waiting to be sorted
        <root>/Sorted/              Year/Country/City/ output
        <root>/Sorted/_Unknown/     files missing a date or a location
        <root>/Duplicates/          exact copies of files already in Sorted
        <root>/app/                 Python runtimes, ExifTool, geodata, state and logs
    """

    def __init__(self, root: Path | str):
        self.root: Path = Path(root).resolve()

    @classmethod
    def from_repo_location(cls) -> "AppPaths | None":
        """
        When the code lives at <root>/app/image-sorter/, the root is two levels up.
        Returns None when the code is not installed on a drive (for example in a dev checkout).
        """
        if REPO_DIR.parent.name == "app":
            return cls(REPO_DIR.parent.parent)
        return None

    @property
    def unsorted(self) -> Path:
        return self.root / "Unsorted"

    @property
    def sorted(self) -> Path:
        return self.root / "Sorted"

    @property
    def unknown(self) -> Path:
        return self.sorted / "_Unknown"

    @property
    def duplicates(self) -> Path:
        return self.root / "Duplicates"

    @property
    def app(self) -> Path:
        return self.root / "app"

    @property
    def exiftool_dir(self) -> Path:
        return self.app / "exiftool"

    @property
    def geodata_dir(self) -> Path:
        return self.app / "geodata"

    @property
    def state_db(self) -> Path:
        return self.app / "state" / "state.db"

    def ensure_folders(self) -> None:
        """Create the user-facing folders if they are missing."""
        for folder in (self.unsorted, self.sorted, self.duplicates, self.state_db.parent):
            folder.mkdir(parents=True, exist_ok=True)

    def relative(self, path: Path) -> str:
        """
        Path relative to the drive root with forward slashes.
        Used for everything stored in the state database, since the drive letter
        (or mount point) changes between computers.
        """
        return Path(path).resolve().relative_to(self.root).as_posix()
