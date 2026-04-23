# image-sorter

Image Sorter is a Python CLI tool that reads EXIF metadata from photos and organizes files into a folder hierarchy based on location and date.

## What it does

- Extracts GPS and timestamp metadata from image files.
- Reverse geocodes coordinates into `country` and `city`.
- Organizes images into: `Country/City/Year/Month`.
- Moves files with collision-safe naming (for example, `photo_1.jpg` when needed).
- Tracks processed files in SQLite by SHA-256 hash for idempotent reruns.
- Supports a `--dry-run` mode to preview actions without changing files.
- Supports `--verbose` / `--log-level` for log verbosity control.

## Current status

Implemented:

- Core EXIF read + geocode + organize flow.
- Fail-fast input directory validation.
- Collision-safe move behavior.
- Idempotency state tracking in `.image_sorter/state.db`.
- CLI options for image directory override and dry run.
- Basic unit tests for organization and processing state.

Planned:

- Persist richer metadata records (Postgres goal for learning).
- Add broader test coverage for EXIF/geocoding edge cases.
- Improve geocode caching and retry behavior.

## Configure image directory

Default image directory is defined in:

- `src/utils/image_dir_path.py`

You can override it at runtime with `--image-dir`.

## Usage

Run with default configured directory:

```bash
python main.py
```

Run with explicit directory:

```bash
python main.py --image-dir "C:/path/to/images"
```

Preview without moving files or writing processing state:

```bash
python main.py --dry-run
```

Use both options together:

```bash
python main.py --image-dir "C:/path/to/images" --dry-run
```

Run with detailed debug logs:

```bash
python main.py --verbose
```

Run with an explicit log level:

```bash
python main.py --log-level WARNING
```

## Folder output

Example destination pattern:

```text
<image_dir>/<country>/<city>/<year>/<month>/<filename>
```

When metadata is missing, fallback folders are used:

- `country_unknown`
- `city_unknown`
- `year_unknown`
- `month_unknown`

## Architecture diagrams

- Class model: `assets/architecture/diagrams/class_diagram.wsd`
- Runtime sequence flow: `assets/architecture/diagrams/run_flow.wsd`
- Rendered class diagram: `assets/architecture/diagrams/class_diagram.png`
- Rendered run flow diagram: `assets/architecture/diagrams/run_flow.png`

Regenerate diagram PNG files:

```bash
powershell -ExecutionPolicy Bypass -File scripts/render_diagrams.ps1
```

## Tests

Run tests:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

## Project goals

- Learn Python OOP through a real project.
- Build an image pipeline with safe reruns.
- Add database persistence for deeper learning (Postgres).
