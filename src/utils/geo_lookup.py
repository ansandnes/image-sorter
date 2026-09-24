# Standard Library imports
import logging
import math
from pathlib import Path

# Module imports
from src.utils.classes.GPSCoordinates import GPSCoordinates
from src.utils.classes.Location import Location

CITIES_FILE = "cities.tsv"
COUNTRIES_FILE = "countries.tsv"

# Grid cell size in degrees, and how many rings of cells to search around a point
# before giving up (about 5 * 111 km at the equator).
_CELL_SIZE = 1.0
_MAX_RING = 5

_EARTH_RADIUS_KM = 6371.0

# Used to estimate how far a city's built-up area reaches from its center:
# radius = sqrt(population / (pi * density)). Paris (2.1M) ~15 km, a town of 10k ~1 km.
_URBAN_DENSITY_PER_KM2 = 3000.0


class GeoLookup:
    """
    Offline reverse geocoder: finds the city a GPS position belongs to using
    GeoNames data stored on the drive (built by scripts/build_drive.py).

    Big cities are listed together with their districts ("Paris" and "Paris 04
    Hôtel-de-Ville"), so the nearest entry is not always the best folder name.
    When the position lies within the estimated urban radius of one or more
    places, the most populous of them wins; otherwise the nearest place is used.

    geodata_dir must contain:
        cities.tsv      name <TAB> country_code <TAB> latitude <TAB> longitude <TAB> timezone <TAB> population
        countries.tsv   country_code <TAB> country_name
    """

    def __init__(self, geodata_dir: Path | str):
        self.geodata_dir = Path(geodata_dir)
        self._names: list[str] = []
        self._country_codes: list[str] = []
        self._latitudes: list[float] = []
        self._longitudes: list[float] = []
        self._timezones: list[str] = []
        self._populations: list[int] = []
        self._countries: dict[str, str] = {}
        self._grid: dict[tuple[int, int], list[int]] = {}
        self._loaded = False

    def is_available(self) -> bool:
        return (self.geodata_dir / CITIES_FILE).is_file() and (
            self.geodata_dir / COUNTRIES_FILE
        ).is_file()

    def load(self) -> None:
        """Read the data files into memory and build the grid index."""
        if self._loaded:
            return

        with open(self.geodata_dir / COUNTRIES_FILE, encoding="utf-8") as file_handle:
            for line in file_handle:
                code, _, name = line.rstrip("\n").partition("\t")
                if code:
                    self._countries[code] = name

        with open(self.geodata_dir / CITIES_FILE, encoding="utf-8") as file_handle:
            for line in file_handle:
                parts = line.rstrip("\n").split("\t")
                if len(parts) < 5:
                    continue
                name, country_code, latitude, longitude, timezone_name = parts[:5]
                population = int(parts[5]) if len(parts) > 5 and parts[5].isdigit() else 0
                index = len(self._names)
                self._names.append(name)
                self._country_codes.append(country_code)
                self._latitudes.append(float(latitude))
                self._longitudes.append(float(longitude))
                self._timezones.append(timezone_name)
                self._populations.append(population)
                self._grid.setdefault(_cell(float(latitude), float(longitude)), []).append(index)

        self._loaded = True
        logging.getLogger("main").info(f"Loaded {len(self._names)} cities for offline geocoding")

    def lookup(self, gps: GPSCoordinates) -> Location | None:
        """
        Return the Location for a position, or None when no city is within
        the search radius (for example in the middle of an ocean).
        """
        self.load()

        latitude, longitude = gps.get_latitude(), gps.get_longitude()
        center_row, center_col = _cell(latitude, longitude)

        # (distance in km, index) for every place in the searched cells
        candidates: list[tuple[float, int]] = []
        found_in_ring = None

        for ring in range(_MAX_RING + 1):
            for cell in _ring_cells(center_row, center_col, ring):
                for index in self._grid.get(cell, ()):
                    distance = _haversine_km(
                        latitude, longitude, self._latitudes[index], self._longitudes[index]
                    )
                    candidates.append((distance, index))

            if candidates and found_in_ring is None:
                found_in_ring = ring
            # A closer or bigger city can still sit in the next ring out, so search one extra ring.
            if found_in_ring is not None and ring > found_in_ring:
                break

        if not candidates:
            return None

        best_index = self._choose_city(candidates)
        country_code = self._country_codes[best_index]
        return Location(
            country=self._countries.get(country_code, country_code),
            city=self._names[best_index],
            timezone=self._timezones[best_index] or None,
        )

    def _choose_city(self, candidates: list[tuple[float, int]]) -> int:
        """
        The most populous place whose urban radius covers the position,
        or the nearest place when none does.
        """
        containing = [
            index
            for distance, index in candidates
            if distance <= _urban_radius_km(self._populations[index])
        ]
        if containing:
            return max(containing, key=lambda index: self._populations[index])
        return min(candidates)[1]


def _urban_radius_km(population: int) -> float:
    return math.sqrt(population / (math.pi * _URBAN_DENSITY_PER_KM2))


def _cell(latitude: float, longitude: float) -> tuple[int, int]:
    return (math.floor(latitude / _CELL_SIZE), math.floor(longitude / _CELL_SIZE))


def _ring_cells(center_row: int, center_col: int, ring: int):
    """Yield grid cells forming the square ring at distance `ring` around the center."""
    columns = int(360 / _CELL_SIZE)
    min_col = -int(180 / _CELL_SIZE)

    for row in range(center_row - ring, center_row + ring + 1):
        for col in range(center_col - ring, center_col + ring + 1):
            if max(abs(row - center_row), abs(col - center_col)) != ring:
                continue
            # Wrap longitude around the date line.
            wrapped_col = (col - min_col) % columns + min_col
            yield (row, wrapped_col)


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = phi2 - phi1
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return 2 * _EARTH_RADIUS_KM * math.asin(math.sqrt(a))
