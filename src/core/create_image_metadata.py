# Standard Library imports


# Module imports
from src.utils.classes.ImageMetadata import ImageMetadata
from src.utils.classes.ImageGPS import ImageGPS
from src.utils.convert_coord_to_decimal_number import convert_coord_to_decimal_number
from src.utils.get_location_from_gps import get_location_from_gps
from src.utils.set_logger import set_logger

def create_image_metadata(timestamp: str | None, coords: ImageGPS, image_dir: str, filename: str) -> ImageMetadata:
    """
        This function creates an instance of the ImageMetadata class
        and sets the coordinates and location of the image.
    """

    # Initialize logger
    main_logger = set_logger(name="main", log_path=image_dir, logfilename="main.log", mode="a")

    # Create an instance of the ImageMetadata class
    image_metadata = ImageMetadata(dir=image_dir, name=filename, timestamp=timestamp, coords=coords)

    # Get the GPS coordinates
    latitude = coords.latitude
    latitude_ref = coords.latitude_ref
    longitude = coords.longitude
    longitude_ref = coords.longitude_ref

    # print(latitude, latitude_ref, longitude, longitude_ref)
    
    # Set the GPS coordinates to image_metadata
    image_metadata.set_coords(longitude, longitude_ref, latitude, latitude_ref)

    # Check to ensure the coordinates are in the correct format before processing
    if latitude and latitude_ref and longitude and longitude_ref:

        # Initialize variables
        decimal_latitude = None
        decimal_longitude = None
                
        try:
            # Convert the raw piexif tuple data to a decimal number accounting for ref
            decimal_latitude = convert_coord_to_decimal_number(latitude, latitude_ref)
            decimal_longitude = convert_coord_to_decimal_number(longitude, longitude_ref)

            # Get the location from the GPS coordinates
            location = get_location_from_gps(decimal_latitude, decimal_longitude, image_dir)
            
            # Add location to metadata
            image_metadata.set_location(location)

        except Exception as e:
            # Log the error
            main_logger.error(f"Error: Could not convert GPS coordinates to decimal for {filename}: {e}")

    else:
        # Log the error
        main_logger.error(f"Error: Invalid GPS coordinates for {filename}")

    return image_metadata