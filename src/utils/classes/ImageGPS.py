class ImageGPS:
    def __init__(self, latitude: tuple | None, latitude_ref: bytes | None, longitude: tuple | None, longitude_ref: bytes | None):
        self.latitude : tuple | None = latitude
        self.latitude_ref : bytes | None = latitude_ref
        self.longitude : tuple | None = longitude
        self.longitude_ref : bytes | None = longitude_ref

    def get_coords(self) -> dict:
        return {
            "latitude": self.latitude,
            "latitude_ref": self.latitude_ref,
            "longitude": self.longitude,
            "longitude_ref": self.longitude_ref
        }

    def get_longitude(self) -> tuple | None:
        return self.longitude

    def get_latitude(self) -> tuple | None:
        return self.latitude

    def get_longitude_ref(self) -> bytes | None:
        return self.longitude_ref

    def get_latitude_ref(self) -> bytes | None:
        return self.latitude_ref
