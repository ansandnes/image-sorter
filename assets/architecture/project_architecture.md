# Project Architecture

The project is modular. It runs from a portable drive with no installation. The main components are:

* **Launchers** (`launchers/`): one double-click script per OS. Each picks the portable Python bundled on the drive for the current OS and CPU, then starts `main.py` with the drive root.
* **Metadata reader** (`src/utils/exiftool.py`, `src/utils/timestamps.py`, `src/core/create_image_metadata.py`):
  * ExifTool reads date and GPS tags from photos and videos, in batches.
  * The best capture time is chosen: `DateTimeOriginal` first; for videos, UTC dates are converted to the local time of the place.
* **Geo lookup** (`src/utils/geo_lookup.py`):
  * Offline reverse geocoding against GeoNames data on the drive, using a 1°×1° grid index.
  * Picks the most populous place whose estimated urban radius covers the position, or else the nearest place.
* **Organizer** (`src/core/organize_images.py`):
  * Plans every move first (Sorted / _Unknown / Duplicates) so the user can review it.
  * Then moves files without ever overwriting.
* **Processing state** (`src/core/processing_state.py`): SQLite record of file hashes and destinations, used to detect duplicates on later runs.
* **Drive builder** (`scripts/build_drive.py`):
  * Downloads portable Python builds, ExifTool, GeoNames and tzdata.
  * Lays out the drive.

Design choices:

* **Standard library only.** No compiled third-party packages, so one copy of the source runs on every bundled Python.
* **ExifTool over piexif.** piexif only reads JPEG/TIFF EXIF, while ExifTool covers HEIC, PNG, RAW and video formats.
* **Offline geocoding over Nominatim.** It needs no internet, has no rate limit (Nominatim allows 1 request/second) and gives the same answer every time.
