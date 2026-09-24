# Standard Library imports
import logging
from pathlib import Path

# Module imports
from src.utils.classes.GPSCoordinates import GPSCoordinates
from src.utils.classes.ImageMetadata import ImageMetadata
from src.utils.geo_lookup import GeoLookup
from src.utils.timestamps import pick_capture_time


def create_image_metadata(path: Path, tags: dict, geo_lookup: GeoLookup) -> ImageMetadata:
    """
    Build an ImageMetadata from the ExifTool tags of one file:
    GPS position -> nearest city -> capture time in that city's local time.
    """
    main_logger = logging.getLogger("main")

    image_metadata = ImageMetadata(path=path)

    gps = extract_gps(tags)
    image_metadata.set_gps(gps)

    if gps:
        location = geo_lookup.lookup(gps)
        image_metadata.set_location(location)
        if location is None:
            main_logger.info(f"No city found near {gps} for {path.name}")
    else:
        main_logger.info(f"No GPS information found for {path.name}")

    timezone_name = image_metadata.get_location().get_timezone() if image_metadata.get_location() else None
    image_metadata.set_taken_at(pick_capture_time(tags, timezone_name))

    if image_metadata.get_taken_at() is None:
        main_logger.info(f"No capture date found for {path.name}")

    return image_metadata


def extract_gps(tags: dict) -> GPSCoordinates | None:
    """
    Read a signed decimal GPS position from ExifTool tags (run with -n).
    Composite tags combine the value with its N/S/E/W reference, so they are preferred.
    """
    for group in ("Composite", "XMP"):
        latitude = _to_float(tags.get(f"{group}:GPSLatitude"))
        longitude = _to_float(tags.get(f"{group}:GPSLongitude"))
        if latitude is not None and longitude is not None:
            gps = GPSCoordinates(latitude, longitude)
            return gps if gps.is_valid() else None

    # Videos: "59.9139 10.7522 12.3" (latitude longitude [altitude])
    coordinates = tags.get("QuickTime:GPSCoordinates")
    if isinstance(coordinates, str):
        parts = coordinates.split()
        if len(parts) >= 2:
            latitude, longitude = _to_float(parts[0]), _to_float(parts[1])
            if latitude is not None and longitude is not None:
                gps = GPSCoordinates(latitude, longitude)
                return gps if gps.is_valid() else None

    return None


def _to_float(value) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
