# Standard Library imports
import argparse
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

# Module imports
from src.core.app_paths import AppPaths
from src.core.create_image_metadata import create_image_metadata
from src.core.organize_images import MoveKind, execute_moves, plan_moves
from src.core.processing_state import compute_file_hash, initialize_processing_state
from src.core.scan_unsorted import remove_empty_folders, scan_unsorted
from src.utils.console import Progress, confirm
from src.utils.exiftool import ExifTool, ExifToolNotFoundError, normalize_path
from src.utils.geo_lookup import GeoLookup
from src.utils.set_logger import set_logger


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Sort photos and videos from Unsorted/ into Sorted/<Year>/<Country>/<City>/."
    )
    parser.add_argument(
        "--root",
        help="Drive root containing Unsorted/, Sorted/ and app/. "
        "Defaults to two levels above this program when installed at <root>/app/image-sorter/.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would happen without moving any files.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Do not ask for confirmation before moving files.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set log file verbosity level.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Shortcut for --log-level DEBUG.",
    )
    return parser.parse_args()


def resolve_paths(root_arg: str | None) -> AppPaths | None:
    if root_arg:
        return AppPaths(root_arg)
    return AppPaths.from_repo_location()


def main() -> int:

    # Global Timer
    start_time = time.time()

    args = parse_args()
    log_level_name = "DEBUG" if args.verbose else args.log_level

    paths = resolve_paths(args.root)
    if paths is None or not paths.root.is_dir():
        print("Could not find the drive folder. Start the app with the launcher on the drive, or pass --root.")
        return 2
    paths.ensure_folders()

    # Initialize logger (one log file per run in app/logs/)
    main_logger = set_logger(
        name="main",
        logfilename=f"image-sorter_{datetime.now():%Y-%m-%d_%H-%M-%S}.log",
        log_path=str(paths.app),
        mode="w",
        level=getattr(logging, log_level_name),
    )
    main_logger.info(f"Drive root: {paths.root}")
    main_logger.info(f"Dry run mode: {args.dry_run}")

    print("Image Sorter")
    print(f"  Drive: {paths.root}")
    print()

    # Find files
    media_files, other_files = scan_unsorted(paths.unsorted)
    if not media_files:
        if not args.dry_run:
            remove_empty_folders(paths.unsorted)
        print("The Unsorted folder has no photos or videos. Nothing to do.")
        _report_other_files(paths, other_files)
        return 0
    print(f"Found {len(media_files)} photos/videos in Unsorted.")

    # Tools
    try:
        exiftool = ExifTool(paths.exiftool_dir)
    except ExifToolNotFoundError as error:
        print(f"ERROR: {error}")
        main_logger.error(str(error))
        return 1
    main_logger.info(f"ExifTool: {' '.join(exiftool.command)} (version {exiftool.version()})")

    geo_lookup = GeoLookup(paths.geodata_dir)
    if not geo_lookup.is_available():
        print(f"ERROR: Location data is missing from {paths.geodata_dir}. Rebuild the drive with scripts/build_drive.py.")
        return 1
    geo_lookup.load()

    db_path = initialize_processing_state(paths.state_db)
    main_logger.info(f"State database: {db_path}")

    # Read metadata and hash every file
    tags_by_path = exiftool.read_tags(media_files, Progress("Reading dates and locations"))

    items = []
    hashing_progress = Progress("Checking for duplicates")
    for number, file_path in enumerate(media_files, start=1):
        try:
            file_hash = compute_file_hash(str(file_path))
        except OSError as error:
            main_logger.error(f"Failed to read {file_path}: {error}")
            print(f"\n  Could not read {file_path.name}: {error}")
            continue
        tags = tags_by_path.get(normalize_path(file_path), {})
        items.append((create_image_metadata(file_path, tags, geo_lookup), file_hash))
        hashing_progress(number, len(media_files))

    # Plan and preview
    planned = plan_moves(paths, items, db_path)
    _print_plan_summary(planned)

    if args.dry_run:
        for move in planned:
            print(f"  {paths.relative(move.source)}  ->  {paths.relative(move.destination)}")
        print("\nDry run: no files were moved.")
        return 0

    if not args.yes and not confirm("\nMove the files now?"):
        print("Cancelled. No files were moved.")
        return 0

    # Move
    result = execute_moves(paths, planned, db_path, Progress("Moving files"))
    remove_empty_folders(paths.unsorted)

    print()
    print("Done.")
    print(f"  Sorted:     {result.moved[MoveKind.SORTED]}")
    print(f"  _Unknown:   {result.moved[MoveKind.UNKNOWN]}   (sort these by hand from Sorted/_Unknown)")
    print(f"  Duplicates: {result.moved[MoveKind.DUPLICATE]}")
    if result.failed:
        print(f"  Failed:     {len(result.failed)}   (left in Unsorted, see the log in app/logs)")
        for source, error in result.failed:
            print(f"    {source.name}: {error}")
    _report_other_files(paths, other_files)

    # Global Timer
    elapsed = time.time() - start_time
    main_logger.info(f"Total time taken: {elapsed:.1f} seconds")
    print(f"\nTotal time: {elapsed:.1f} seconds")
    return 1 if result.failed else 0


def _print_plan_summary(planned) -> None:
    counts = {kind: 0 for kind in MoveKind}
    for move in planned:
        counts[move.kind] += 1

    print()
    print("Plan:")
    print(f"  {counts[MoveKind.SORTED]:>6}  to Sorted/<Year>/<Country>/<City>")
    print(f"  {counts[MoveKind.UNKNOWN]:>6}  to Sorted/_Unknown (missing date or location)")
    print(f"  {counts[MoveKind.DUPLICATE]:>6}  to Duplicates (already in Sorted)")


def _report_other_files(paths: AppPaths, other_files: list[Path]) -> None:
    if other_files:
        print(f"\n{len(other_files)} file(s) in Unsorted are not photos/videos and were left there:")
        for file_path in other_files[:10]:
            print(f"  {paths.relative(file_path)}")
        if len(other_files) > 10:
            print(f"  ... and {len(other_files) - 10} more")


if __name__ == "__main__":
    sys.exit(main())
