# Standard Library imports
import os
import logging
from pathlib import Path
from datetime import datetime

# Module imports
from src.utils.classes.ImageMetadata import ImageMetadata

def _get_unique_destination(destination: Path) -> Path:
    """
    Return a non-colliding file path by adding a numeric suffix when needed.
    """
    if not destination.exists():
        return destination

    stem = destination.stem
    suffix = destination.suffix
    parent = destination.parent
    index = 1

    while True:
        candidate = parent / f"{stem}_{index}{suffix}"
        if not candidate.exists():
            return candidate
        index += 1

def _decode_timestamp(timestamp: str | bytes | None) -> str:
    """
    Normalize EXIF timestamp input to a string.
    """
    if timestamp is None:
        return ""
    if isinstance(timestamp, bytes):
        return timestamp.decode(errors="ignore").strip()
    return str(timestamp).strip()

def _extract_year_month(timestamp: str | bytes | None) -> tuple[str, str]:
    """
    Extract year and month from EXIF timestamp.
    Falls back to unknown placeholders when parsing fails.
    """
    timestamp_value = _decode_timestamp(timestamp)
    if not timestamp_value:
        return ("year_unknown", "month_unknown")

    supported_formats = (
        "%Y:%m:%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y:%m:%d",
        "%Y-%m-%d",
    )

    for date_format in supported_formats:
        try:
            parsed = datetime.strptime(timestamp_value, date_format)
            return (f"{parsed.year:04d}", f"{parsed.month:02d}")
        except ValueError:
            continue

    return ("year_unknown", "month_unknown")

def organize_images(
    image_dir: str, image_metadata: ImageMetadata, filename: str, dry_run: bool = False
) -> str | None:
    """
    Organize one image into country/city/year/month folder tree.
    Returns destination path when move succeeds, otherwise None.
    """
    main_logger = logging.getLogger("main")

    # Initialize variables
    image_dir_path = Path(image_dir)
    country = f"{image_metadata.get_location().get_country()}"
    city = f"{image_metadata.get_location().get_city()}"
    year, month = _extract_year_month(image_metadata.get_timestamp())
    new_folder_country = image_dir_path / country
    new_folder_city = new_folder_country / city
    new_folder_year = new_folder_city / year
    new_folder_month = new_folder_year / month
    source_path = image_dir_path / filename
    destination_path = _get_unique_destination(new_folder_month / filename)

    # Create a new folder based on the country
    if not new_folder_country.exists():
        try:
            os.makedirs(new_folder_country)

        except Exception as e:
            main_logger.error(f"Failed to create {new_folder_country}: {e}")

    # Create a new folder based on the city
    if not new_folder_city.exists():
        try:
            os.makedirs(new_folder_city)
        
        except Exception as e:
            main_logger.error(f"Failed to create {new_folder_city}: {e}")


    # Create a new folder based on year
    if not new_folder_year.exists():
        try:
            os.makedirs(new_folder_year)

        except Exception as e:
            main_logger.error(f"Failed to create {new_folder_year}: {e}")

    # Create a new folder based on month
    if not new_folder_month.exists():
        try:
            os.makedirs(new_folder_month)

        except Exception as e:
            main_logger.error(f"Failed to create {new_folder_month}: {e}")

    if dry_run:
        main_logger.info(f"[DRY RUN] Would move {filename} to {destination_path}")
        return str(destination_path)

    # Move the image to the new folder
    if new_folder_month.exists():
        # Move the image to the new folder
        try:
            # Move image without overwriting existing files.
            os.replace(source_path, destination_path)

            # Log that the image was moved to the new folder
            main_logger.info(f"Moved {filename} to {destination_path.parent}")
            return str(destination_path)

        except Exception as e:
            main_logger.error(f"Failed to move {filename} to {new_folder_month}: {e}")
            return None

    return None
