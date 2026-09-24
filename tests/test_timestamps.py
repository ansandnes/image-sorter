import unittest
from datetime import datetime, timedelta, timezone

from src.utils.timestamps import parse_timestamp, pick_capture_time, utc_to_local


class TestParseTimestamp(unittest.TestCase):
    def test_exif_format(self) -> None:
        self.assertEqual(parse_timestamp("2024:07:15 09:30:00"), (datetime(2024, 7, 15, 9, 30), None))

    def test_iso_format_with_fraction_and_offset(self) -> None:
        parsed, offset = parse_timestamp("2024-07-15T09:30:00.123+02:00")
        self.assertEqual(parsed, datetime(2024, 7, 15, 9, 30))
        self.assertEqual(offset, timezone(timedelta(hours=2)))

    def test_utc_suffix(self) -> None:
        self.assertEqual(parse_timestamp("2024:07:15 07:30:00Z")[1], timezone.utc)

    def test_date_only(self) -> None:
        self.assertEqual(parse_timestamp("2024:07:15")[0], datetime(2024, 7, 15))

    def test_rejects_empty_zero_and_garbage(self) -> None:
        for value in (None, "", "0000:00:00 00:00:00", "1904:01:01 00:00:00", "not a date", "2024:13:40 00:00:00"):
            self.assertIsNone(parse_timestamp(value), value)


class TestPickCaptureTime(unittest.TestCase):
    def test_prefers_date_time_original_over_create_date(self) -> None:
        tags = {
            "EXIF:CreateDate": "2024:07:16 10:00:00",
            "EXIF:DateTimeOriginal": "2024:07:15 09:30:00",
        }
        self.assertEqual(pick_capture_time(tags), datetime(2024, 7, 15, 9, 30))

    def test_apple_creation_date_keeps_local_wall_clock(self) -> None:
        tags = {
            "QuickTime:CreationDate": "2024:07:15 09:30:00+02:00",
            "QuickTime:CreateDate": "2024:07:15 07:30:00",
        }
        self.assertEqual(pick_capture_time(tags), datetime(2024, 7, 15, 9, 30))

    def test_quicktime_utc_converted_to_place_timezone(self) -> None:
        tags = {"QuickTime:CreateDate": "2024:01:01 03:00:00"}
        self.assertEqual(
            pick_capture_time(tags, "America/New_York"), datetime(2023, 12, 31, 22, 0)
        )

    def test_no_dates(self) -> None:
        self.assertIsNone(pick_capture_time({"QuickTime:CreateDate": "0000:00:00 00:00:00"}))

    def test_unknown_timezone_falls_back_to_computer_timezone(self) -> None:
        utc_time = datetime(2024, 1, 1, 3, 0)
        expected = utc_time.replace(tzinfo=timezone.utc).astimezone().replace(tzinfo=None)
        self.assertEqual(utc_to_local(utc_time, "Not/AZone"), expected)


if __name__ == "__main__":
    unittest.main()
