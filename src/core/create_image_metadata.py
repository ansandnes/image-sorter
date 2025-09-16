# Module imports
from src.utils.get_image_coords import get_image_coords
from src.utils.get_location_from_gps import get_location_from_gps
from src.utils.convert_coord_to_decimal_number import convert_coord_to_decimal_number


def create_image_metadata(image_dir):
    """
        Creates a dictionary of image metadata, including GPS coordinates and location information.

        Args:
            image_dir (str): The path to the directory containing the images.

        Returns:
            dict: A dictionary containing the image metadata.
    """
    
    # Create a dictionary to store image metadata
    image_metadata = {}

    # Get image GPS coordinates
    image_gps_coords = get_image_coords(image_dir)

    # Use the GPS details of each image to find the location
    for image in image_gps_coords.items():
        longitude = image[1]["longitude"]
        latitude = image[1]["latitude"]
        altitude = image[1]["altitude"]
        longitude_ref = image[1]["longitude_ref"]
        latitude_ref = image[1]["latitude_ref"]
        
        gps = {"gps": {
            "longitude": longitude,
            "latitude": latitude,
            "altitude": altitude,
            "longitude_ref": longitude_ref,
            "latitude_ref": latitude_ref
        }}

        # Add the GPS coordinates to the image metadata dictionary
        image_metadata[image[0]] = gps
        
        # Check to ensure the coordinates are in the correct format before processing
        if isinstance(latitude, tuple) and isinstance(longitude, tuple):
            try:
                # Convert the raw piexif tuple data to a decimal number
                decimal_latitude = convert_coord_to_decimal_number(latitude, latitude_ref)
                decimal_longitude = convert_coord_to_decimal_number(longitude, longitude_ref)
            except Exception as e:
                print(f"Error: Could not convert GPS coordinates to decimal: {e}")
                continue
            try:
                # Get the location from the GPS coordinates
                location = get_location_from_gps(decimal_latitude, decimal_longitude)

                # Merge the location data into the existing dictionary
                if location:
                    image_metadata[image[0]].update(location)
                    
            except Exception as e:
                print(f"Error: Could not find location from GPS coordinates: {e}")
        else:
            print(f"Skipping image with invalid GPS data: {image[0]}")
        
    return image_metadata