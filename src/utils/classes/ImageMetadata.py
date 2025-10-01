# Standard Library Imports
from datetime import datetime
from typing import Tuple, List, Dict, Optional, Any

# Module Imports
from src.utils.classes.ImagePath import ImagePath
from src.utils.classes.ImageTimestamp import ImageTimestamp
from src.utils.classes.Location import Location

class ImageMetadata:

    def __init__(self, image_id: int, coords: Dict[str, Any]):
        """  """

        # Attributes
        self.image_id : int = image_id
        self.coords : Dict[str, Any] = coords

        # Composition attributes
        self.path : Optional[ImagePath] = None
        self.timestamp : Optional[ImageTimestamp] = None
        self.location : Optional[Location] = None

    # Method to set image metadata
    def set_metadata(self):
        metadata = {
            "image_id": self.image_id,
            "path": self.path,
            "timestamp": self.timestamp,
            "coords": self.coords,
            "location": self.location
        }

        return metadata