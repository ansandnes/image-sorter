# Standard Library Imports
from dataclasses import dataclass
from datetime import datetime

# Module Imports
from src.utils.classes.ImageTimestamp import ImageTimestamp
from src.utils.classes.ImageGPS import ImageGPS
from src.utils.classes.Location import Location


class ImageMetadata:

    def __init__(self, image_dir):
        """  """
        self.image_dir: str = image_dir
        self.image_name: str | None = None
        self.image_timestamp: ImageTimestamp | None = None
        self.image_coords: ImageGPS | None = None
        self.image_location: Location | None = None

    def set_name(self, name):
        """  """
        self.image_name = name
        return self.image_name
    
    def set_timestamp(self, timestamp):
        """  """
        self.image_timestamp = timestamp
        return self.image_timestamp

    def set_coords(self, latitude, latitude_ref, longitude, longitude_ref):
        """  """
        self.image_coords = ImageGPS(latitude, latitude_ref, longitude, longitude_ref)
        return self.image_coords

    def set_location(self, location):
        """  """
        self.image_location = location
        return self.image_location
    
    def get_name(self):
        """  """
        return self.image_name
    
    def get_timestamp(self):
        """  """
        return self.image_timestamp

    def get_coords(self):
        """  """
        return self.image_coords
    
    def get_location(self):
        """  """
        return self.image_location
    
    