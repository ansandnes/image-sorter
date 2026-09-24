# image-sorter

Image Sorter is a portable tool that lives on a USB drive and sorts photos and videos
into folders by **when** and **where** they were taken:

```text
Sorted/<Year>/<Country>/<City>/2024-07-15_09-30-00_IMG_1234.jpg
```

Double-click the launcher on the drive. It runs on Windows, macOS and Linux without
installing anything, and works offline.

## How it works

1. Drop photos and videos in `Unsorted/` (subfolders are fine).
2. Double-click the launcher:
   - Windows: `Start-ImageSorter.bat`
   - macOS: `Start-ImageSorter.command`
   - Linux: `start-image-sorter.sh`
3. The app shows a plan and asks `Move the files now? [y/N]`.

| Where | What |
|-------|------|
| `Sorted/<Year>/<Country>/<City>/` | Files with both a capture date and a GPS location. Names are prefixed with the capture time so they list in date order. |
| `Sorted/_Unknown/` | Files missing a date and/or a location. Sort these by hand. Files with a date still get the date prefix. |
| `Duplicates/` | Exact copies (same SHA-256) of files already in `Sorted/`. |
| `Unsorted/` | Anything that isn't a photo or video is left here. |

Details:

- **Metadata** is read with [ExifTool](https://exiftool.org). It supports JPEG, HEIC, PNG, WebP, TIFF, camera RAW, MP4, MOV and more.
  - The capture date prefers `DateTimeOriginal`.
  - Video dates stored in UTC are converted to the local time of where the video was taken.
- **Location** comes from offline reverse geocoding against [GeoNames](https://www.geonames.org) places with 1000+ inhabitants.
  - A position inside a big city's area gets the city name ("Paris", not "Paris 04 Hôtel-de-Ville").
  - Elsewhere the nearest place is used.
- **Safe reruns:**
  - Files are never overwritten; name clashes get `_1`, `_2`, ...
  - Sorted files are recorded in `app/state/state.db`, with paths relative to the drive so a changing drive letter doesn't matter.
  - An identical file added later goes to `Duplicates/`. If the earlier copy was removed from `Sorted/`, it is sorted again instead.

## Drive layout

```text
<drive>/
├── Start-ImageSorter.bat          Windows launcher
├── Start-ImageSorter.command      macOS launcher
├── start-image-sorter.sh          Linux launcher
├── HOW-TO-USE.txt
├── Unsorted/   Sorted/   Duplicates/
└── app/
    ├── image-sorter/              this program (main.py + src/)
    ├── python/<platform>/         portable Python for windows-x64, macos-arm64, macos-x64, linux-x64, linux-arm64
    ├── exiftool/windows|perl/     ExifTool (Windows exe; Perl script for macOS/Linux)
    ├── geodata/                   cities.tsv, countries.tsv
    ├── lib/tzdata/                timezone database (needed on Windows)
    ├── state/state.db             record of sorted files
    └── logs/                      one log file per run
```

## Building the drive

Needs Python 3.10+ and internet access, and uses only the standard library:

```bash
python scripts/build_drive.py
```

This downloads the portable Pythons ([python-build-standalone](https://github.com/astral-sh/python-build-standalone)), ExifTool, GeoNames data and `tzdata` into `dist/.cache/`. It assembles the drive in `dist/ImageSorter/` (about 270 MB).

- **Put it on a drive:** copy the contents of `dist/ImageSorter/` to the root of the drive.
- **Update an existing drive:** pass it as the output, e.g. `--out E:\`. Only program files are replaced; `Unsorted/`, `Sorted/`, `Duplicates/`, `app/state/` and `app/logs/` are kept.

Options:

- `--platforms windows-x64,macos-arm64`: bundle only some runtimes to save space.
- `--no-python`: bundle no Python; the launchers use the computer's `python3`/`python`.
- `--cities 5000`: use bigger towns only, which gives fewer, larger city folders.

Format the drive as **exFAT** so all three operating systems can read and write it.

## Running from source

```bash
python main.py --root /path/to/drive-folder --dry-run
```

| Option | Meaning |
|--------|---------|
| `--root` | Folder containing `Unsorted/` and `app/`. The launchers pass this automatically. |
| `--dry-run` | List planned moves without moving anything. |
| `--yes` | Don't ask for confirmation. |
| `--verbose` / `--log-level` | Log file detail. |

ExifTool is found in `<root>/app/exiftool/`, via the `IMAGE_SORTER_EXIFTOOL` environment variable, or on `PATH`.

## Tests

```bash
python -m unittest
```

The end-to-end test needs ExifTool. It skips itself when none is found. Run `scripts/build_drive.py` once, or install `exiftool`.

## Architecture diagrams

- Class model: `assets/architecture/diagrams/class_diagram.wsd` (`.png`)
- Runtime sequence flow: `assets/architecture/diagrams/run_flow.wsd` (`.png`)

Regenerate the PNG files on Windows:

```bash
powershell -ExecutionPolicy Bypass -File scripts/render_diagrams.ps1
```

## Project goals

- Learn Python OOP through a real project.
- Build an image pipeline with safe reruns.
- Possible next step: persist richer metadata records (Postgres) for deeper learning.

## Credits

- [ExifTool](https://exiftool.org) by Phil Harvey.
- Location data from [GeoNames](https://www.geonames.org) (CC BY 4.0).
