# Standard Library Imports
from typing import Tuple, List, Dict, Optional
import uuid # For generating unique IDs if not using a database sequence

class ImagePath:
    def __init__(self,
        latitude: Tuple[float, float, float],
        latitude_ref: str,
        longitude: Tuple[float, float, float],
        longitude_ref: str
        ):
        """  """
        
        self.latitude : Tuple[float, float, float] = latitude
        self.latitude_ref : str = latitude_ref
        self.longitude : Tuple[float, float, float] = longitude
        self.longitude_ref : str = longitude_ref

        def get_coords(self) -> Dict[str, Tuple[float, float, float]]:
            """  """

            coords = {
                "latitude": self.latitude,
                "latitude_ref": self.latitude_ref,
                "longitude": self.longitude,
                "longitude_ref": self.longitude_ref
            }

            return coords