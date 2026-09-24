class GPSCoordinates:
    """
    A GPS position in signed decimal degrees (south and west are negative).
    """

    def __init__(self, latitude: float, longitude: float):
        self.latitude: float = latitude
        self.longitude: float = longitude

    def get_latitude(self) -> float:
        return self.latitude

    def get_longitude(self) -> float:
        return self.longitude

    def is_valid(self) -> bool:
        """
        Reject out-of-range values and the 0,0 position that cameras
        often write when they have no GPS fix.
        """
        if not (-90 <= self.latitude <= 90 and -180 <= self.longitude <= 180):
            return False
        return not (abs(self.latitude) < 1e-6 and abs(self.longitude) < 1e-6)

    def __repr__(self) -> str:
        return f"GPSCoordinates({self.latitude:.6f}, {self.longitude:.6f})"
