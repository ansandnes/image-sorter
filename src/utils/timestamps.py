# Standard Library imports
import re
from datetime import datetime, timedelta, timezone

# "2024:07:15 09:30:00", "2024-07-15T09:30:00.123+02:00", "2024:07:15 07:30:00Z", "2024:07:15"
_TIMESTAMP_PATTERN = re.compile(
    r"^(\d{4})[:\-](\d{2})[:\-](\d{2})"
    r"(?:[ T](\d{2}):(\d{2})(?::(\d{2}))?(?:\.\d+)?)?"
    r"\s*(Z|[+\-]\d{2}:?\d{2})?$"
)

# Tags holding the local wall-clock time at the place the photo/video was taken,
# in order of preference.
LOCAL_TIME_TAGS = (
    "EXIF:DateTimeOriginal",
    "QuickTime:CreationDate",   # Apple devices; local time with UTC offset
    "XMP:DateTimeOriginal",
    "XMP:DateCreated",
    "EXIF:CreateDate",
    "PNG:CreationTime",
)

# QuickTime/MP4 tags that by specification hold UTC time.
UTC_TIME_TAGS = (
    "QuickTime:CreateDate",
    "QuickTime:MediaCreateDate",
    "QuickTime:TrackCreateDate",
)


def parse_timestamp(value) -> tuple[datetime, timezone | None] | None:
    """
    Parse a metadata date string into (naive wall-clock datetime, UTC offset or None).
    Returns None for empty, zeroed ("0000:00:00 00:00:00") or unparseable values.
    """
    if value is None:
        return None

    match = _TIMESTAMP_PATTERN.match(str(value).strip())
    if not match:
        return None

    year, month, day, hour, minute, second, offset = match.groups()
    try:
        parsed = datetime(
            int(year), int(month), int(day),
            int(hour or 0), int(minute or 0), int(second or 0),
        )
    except ValueError:
        return None

    # Unset camera clocks and QuickTime's "zero" epoch show up as 1904/1970 or earlier.
    if parsed.year < 1971:
        return None

    return (parsed, _parse_offset(offset))


def _parse_offset(offset: str | None) -> timezone | None:
    if not offset:
        return None
    if offset == "Z":
        return timezone.utc
    sign = -1 if offset[0] == "-" else 1
    digits = offset[1:].replace(":", "")
    delta = timedelta(hours=int(digits[:2]), minutes=int(digits[2:]))
    return timezone(sign * delta)


def utc_to_local(utc_time: datetime, timezone_name: str | None) -> datetime:
    """
    Convert a naive UTC datetime to naive local time.
    Uses the timezone of the place the file was taken when known,
    otherwise the timezone of the computer running the sorter.
    """
    aware = utc_time.replace(tzinfo=timezone.utc)

    if timezone_name:
        try:
            from zoneinfo import ZoneInfo
            return aware.astimezone(ZoneInfo(timezone_name)).replace(tzinfo=None)
        except Exception:
            # Timezone database missing (tzdata not installed) or unknown zone name.
            pass

    return aware.astimezone().replace(tzinfo=None)


def pick_capture_time(tags: dict, timezone_name: str | None = None) -> datetime | None:
    """
    Choose the best capture time from ExifTool tags (keys like "EXIF:DateTimeOriginal").
    Returns a naive datetime in the local time of where the file was taken.
    """
    for tag in LOCAL_TIME_TAGS:
        parsed = parse_timestamp(tags.get(tag))
        if parsed:
            # The wall-clock part is already local; any offset is informational.
            return parsed[0]

    for tag in UTC_TIME_TAGS:
        parsed = parse_timestamp(tags.get(tag))
        if parsed:
            wall_clock, offset = parsed
            if offset is not None and offset != timezone.utc:
                # Some cameras write local time with an explicit offset here.
                return wall_clock
            return utc_to_local(wall_clock, timezone_name)

    return None
