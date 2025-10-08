# Module imports
from src.utils.get_image_coords import get_image_coords
from src.utils.convert_coord_to_decimal_number import convert_coord_to_decimal_number
from src.utils.get_location_from_gps import get_location_from_gps


def create_image_metadata(dict_object: dict) -> dict:
    """
        Creates a dictionary of image metadata, including GPS coordinates and location information.

        Args:
            dict_object (dict): A dictionary containing the image metadata.

        Returns:
            dict: A dictionary containing the image metadata.
    """
    
    # Create a dictionary to store image metadata
    image_metadata = {}

    print("\n", "dict_object:\n", dict_object, "\n")

    for key, value in dict_object.items():

        # Get the GPS coordinates
        longitude = value.get_longitude()
        longitude_ref = value.get_longitude_ref()
        latitude = value.get_latitude()
        latitude_ref = value.get_latitude_ref()
        
        # Check to ensure the coordinates are in the correct format before processing
        if isinstance(latitude, tuple) and isinstance(longitude, tuple):
            try:
                # Convert the raw piexif tuple data to a decimal number accounting for ref
                decimal_latitude = convert_coord_to_decimal_number(latitude, latitude_ref)
                decimal_longitude = convert_coord_to_decimal_number(longitude, longitude_ref)
            except Exception as e:
                print(f"Error: Could not convert GPS coordinates to decimal: {e}")
                continue
            try:
                # Get the location from the GPS coordinates
                location = get_location_from_gps(decimal_latitude, decimal_longitude)
                print("\n", "location:\n", location, "\n")

                # Merge the location data into the existing dictionary
                dict_object[key]["location"] = location
                    
            except Exception as e:
                print(f"Error: Could not find location from GPS coordinates: {e}")
        else:
                print(f"Skipping image with invalid GPS data: {key}")
        
    return dict_object