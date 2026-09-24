import shutil
import tempfile
import unittest
from pathlib import Path

from src.utils.classes.GPSCoordinates import GPSCoordinates
from src.utils.geo_lookup import GeoLookup
from tests.helpers import write_geodata


class TestGeoLookup(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp_dir = tempfile.mkdtemp()
        write_geodata(Path(cls.temp_dir))
        cls.geo = GeoLookup(cls.temp_dir)

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.temp_dir, ignore_errors=True)

    def lookup(self, latitude: float, longitude: float):
        return self.geo.lookup(GPSCoordinates(latitude, longitude))

    def test_nearest_city_and_country(self) -> None:
        location = self.lookup(69.65, 18.96)
        self.assertEqual((location.get_country(), location.get_city()), ("Norway", "Tromsø"))
        self.assertEqual(location.get_timezone(), "Europe/Oslo")

    def test_southern_and_western_hemisphere(self) -> None:
        self.assertEqual(self.lookup(-22.9068, -43.1729).get_city(), "Rio de Janeiro")

    def test_district_is_absorbed_by_big_city(self) -> None:
        # Right next to the "Paris 04" district entry, but inside Paris.
        self.assertEqual(self.lookup(48.8545, 2.3575).get_city(), "Paris")

    def test_separate_suburb_keeps_its_own_name(self) -> None:
        self.assertEqual(self.lookup(59.891, 10.525).get_city(), "Sandvika")

    def test_search_wraps_around_date_line(self) -> None:
        self.assertEqual(self.lookup(-16.8, -179.9).get_city(), "Savusavu")

    def test_open_ocean_returns_none(self) -> None:
        self.assertIsNone(self.lookup(30.0, -40.0))


class TestGPSCoordinates(unittest.TestCase):
    def test_null_island_and_out_of_range_are_invalid(self) -> None:
        self.assertFalse(GPSCoordinates(0.0, 0.0).is_valid())
        self.assertFalse(GPSCoordinates(91.0, 10.0).is_valid())
        self.assertTrue(GPSCoordinates(59.9, 10.7).is_valid())


if __name__ == "__main__":
    unittest.main()
