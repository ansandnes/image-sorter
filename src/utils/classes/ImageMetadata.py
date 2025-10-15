# Standard Library Imports

# Module Imports
from src.utils.classes.ImageGPS import ImageGPS
from src.utils.classes.Location import Location


class ImageMetadata:

    def __init__(self, dir: str | None, name: str | None, timestamp: str | None, coords: ImageGPS):
        """  """
        self.dir: str | None = dir
        self.name: str | None = name
        self.timestamp: str | None = timestamp
        self.coords: ImageGPS = coords
        self.location: Location = Location("country_unknown", "city_unknown")

    def set_coords(self, longitude, longitude_ref, latitude, latitude_ref):
        """  """
        self.coords = ImageGPS(latitude, latitude_ref, longitude, longitude_ref)
        return self.coords

    def set_location(self, location: Location):
        """  """
        self.location = location
        return self.location
    
    def get_name(self):
        """  """
        return self.name
    
    def get_timestamp(self):
        """  """
        return self.timestamp

    def get_coords(self):
        """  """
        return self.coords
    
    def get_location(self):
        """  """
        return self.location
    
    