class ImageGPS:
    def __init__(self,
        latitude: tuple,
        latitude_ref: str,
        longitude: tuple,
        longitude_ref: str
        ):
        self.latitude : tuple = latitude
        self.latitude_ref : str = latitude_ref
        self.longitude : tuple = longitude
        self.longitude_ref : str = longitude_ref

    def get_coords(self) -> dict:
        
        coords = {
            "latitude": self.latitude,
            "latitude_ref": self.latitude_ref,
            "longitude": self.longitude,
            "longitude_ref": self.longitude_ref
        }
        return coords


    def get_longitude(self) -> tuple:
        return self.longitude

    def get_latitude(self) -> tuple:
        return self.latitude

    def get_longitude_ref(self) -> str:
        return self.longitude_ref

    def get_latitude_ref(self) -> str:
        return self.latitude_ref
    
    def set_location(self, location_id, country, city):
        self.location_id = location_id
        self.country = country
        self.city = city