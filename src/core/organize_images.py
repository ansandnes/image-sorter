# Standard Library imports
import logging
import shutil
from enum import Enum
from pathlib import Path
from typing import Callable

# Module imports
from src.core.app_paths import AppPaths
from src.core.processing_state import get_recorded_destination, record_processed_image
from src.utils.classes.ImageMetadata import ImageMetadata
from src.utils.naming import dated_filename, path_key, safe_folder_name, unique_destination


class MoveKind(Enum):
    SORTED = "sorted"
    UNKNOWN = "unknown"
    DUPLICATE = "duplicate"


class PlannedMove:
    """One file and where it will go."""

    def __init__(
        self,
        source: Path,
        destination: Path,
        kind: MoveKind,
        file_hash: str,
        reason: str = "",
    ):
        self.source: Path = source
        self.destination: Path = destination
        self.kind: MoveKind = kind
        self.file_hash: str = file_hash
        self.reason: str = reason

    def __repr__(self) -> str:
        return f"PlannedMove({self.source.name} -> {self.destination}, {self.kind.value})"


class MoveResult:
    """Counts from executing a plan."""

    def __init__(self):
        self.moved: dict[MoveKind, int] = {kind: 0 for kind in MoveKind}
        self.failed: list[tuple[Path, str]] = []


def target_path(paths: AppPaths, image_metadata: ImageMetadata) -> tuple[Path, MoveKind, str]:
    """
    Decide where a file belongs:
        Sorted/<Year>/<Country>/<City>/<date>_<name>   when date and location are known
        Sorted/_Unknown/<date>_<name>                  otherwise (date prefix only if known)
    Returns (destination path, kind, reason for Unknown).
    """
    taken_at = image_metadata.get_taken_at()
    location = image_metadata.get_location()
    filename = dated_filename(image_metadata.get_name(), taken_at)

    if taken_at is None or location is None:
        missing = [label for label, value in (("date", taken_at), ("location", location)) if value is None]
        return paths.unknown / filename, MoveKind.UNKNOWN, "no " + " and no ".join(missing)

    folder = (
        paths.sorted
        / f"{taken_at.year:04d}"
        / safe_folder_name(location.get_country(), "Unknown country")
        / safe_folder_name(location.get_city(), "Unknown city")
    )
    return folder / filename, MoveKind.SORTED, ""


def plan_moves(
    paths: AppPaths,
    items: list[tuple[ImageMetadata, str]],
    db_path: str,
) -> list[PlannedMove]:
    """
    Plan a move for every (metadata, file hash) pair without touching any files.
    A file is a duplicate when an identical file (same hash) is already in Sorted,
    or appears earlier in this same run.
    """
    main_logger = logging.getLogger("main")

    planned: list[PlannedMove] = []
    taken: set[str] = set()
    hashes_in_run: dict[str, Path] = {}

    for image_metadata, file_hash in items:
        source = image_metadata.get_path()
        duplicate_of = _find_duplicate(paths, db_path, file_hash, hashes_in_run)

        if duplicate_of:
            destination = unique_destination(paths.duplicates / source.name, taken)
            move = PlannedMove(source, destination, MoveKind.DUPLICATE, file_hash, f"same as {duplicate_of}")
        else:
            destination, kind, reason = target_path(paths, image_metadata)
            destination = unique_destination(destination, taken)
            move = PlannedMove(source, destination, kind, file_hash, reason)
            hashes_in_run[file_hash] = destination

        taken.add(path_key(move.destination))
        planned.append(move)
        main_logger.debug(f"Planned {move}")

    return planned


def _find_duplicate(
    paths: AppPaths, db_path: str, file_hash: str, hashes_in_run: dict[str, Path]
) -> str | None:
    if file_hash in hashes_in_run:
        return paths.relative(hashes_in_run[file_hash])

    recorded = get_recorded_destination(db_path, file_hash)
    # Only a duplicate if the earlier copy is still there; if the user has deleted
    # or moved it, sort this file again rather than hiding it in Duplicates.
    if recorded and (paths.root / recorded).exists():
        return recorded
    return None


def execute_moves(
    paths: AppPaths,
    planned: list[PlannedMove],
    db_path: str,
    progress: Callable[[int, int], None] | None = None,
) -> MoveResult:
    """
    Move the files as planned and record sorted files in the state database.
    """
    main_logger = logging.getLogger("main")
    result = MoveResult()

    for number, move in enumerate(planned, start=1):
        try:
            move.destination.parent.mkdir(parents=True, exist_ok=True)
            # Re-check in case something appeared since planning; never overwrite.
            destination = unique_destination(move.destination)
            shutil.move(str(move.source), str(destination))
            main_logger.info(f"Moved {move.source} -> {destination} ({move.kind.value})")

            if move.kind is not MoveKind.DUPLICATE:
                record_processed_image(
                    db_path=db_path,
                    file_hash=move.file_hash,
                    original_path=paths.relative(move.source),
                    destination_path=paths.relative(destination),
                )
            result.moved[move.kind] += 1

        except Exception as error:
            main_logger.error(f"Failed to move {move.source} -> {move.destination}: {error}")
            result.failed.append((move.source, str(error)))

        if progress:
            progress(number, len(planned))

    return result
