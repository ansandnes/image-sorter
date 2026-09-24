import logging
from pathlib import Path


def write_geodata(geodata_dir: Path) -> None:
    """
    A handful of GeoNames-style rows: enough to test lookups without the full data set.
    Columns: name, country code, latitude, longitude, timezone, population.
    """
    geodata_dir.mkdir(parents=True, exist_ok=True)
    rows = [
        ("Oslo", "NO", 59.91273, 10.74609, "Europe/Oslo", 580000),
        ("Sandvika", "NO", 59.88917, 10.52262, "Europe/Oslo", 20000),
        ("Tromsø", "NO", 69.6489, 18.95508, "Europe/Oslo", 38980),
        ("Paris", "FR", 48.85341, 2.3488, "Europe/Paris", 2138551),
        ("Paris 04 Hôtel-de-Ville", "FR", 48.85441, 2.35723, "Europe/Paris", 27332),
        ("New York City", "US", 40.71427, -74.00597, "America/New_York", 8804190),
        ("Rio de Janeiro", "BR", -22.90642, -43.18223, "America/Sao_Paulo", 6023699),
        ("Savusavu", "FJ", -16.77917, 179.33222, "Pacific/Fiji", 3372),
    ]
    with open(geodata_dir / "cities.tsv", "w", encoding="utf-8") as file_handle:
        for name, country, latitude, longitude, timezone_name, population in rows:
            file_handle.write(f"{name}\t{country}\t{latitude}\t{longitude}\t{timezone_name}\t{population}\n")
    with open(geodata_dir / "countries.tsv", "w", encoding="utf-8") as file_handle:
        file_handle.write("NO\tNorway\nFR\tFrance\nUS\tUnited States\nBR\tBrazil\nFJ\tFiji\n")


def close_main_logger() -> None:
    logger = logging.getLogger("main")
    for handler in logger.handlers:
        handler.close()
    logger.handlers.clear()
