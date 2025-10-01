# Standard Library Imports
from datetime import datetime

class ImageTimestamp:

    def __init__(self, timestamp: datetime):
        self.timestamp : datetime = timestamp

    def get_timestamp(self) -> datetime:
        """Returns the timestamp of the image as a datetime object."""
        return self.timestamp