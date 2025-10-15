# Module imports
from src.utils.classes.ImageMetadata import ImageMetadata
from src.utils.convert_coord_to_decimal_number import convert_coord_to_decimal_number
from src.utils.get_location_from_gps import get_location_from_gps
from src.utils.set_logger import set_logger

def create_image_metadata(dict_object: dict, image_dir: str) -> ImageMetadata:
    """
         
    """

    # Initialize logger
    main_logger = set_logger(name="main", log_path=image_dir, logfilename="main.log", mode="a")

    # Create an instance of the ImageMetadata class
    image_metadata = ImageMetadata(image_dir)

    for key, value in dict_object.items():
        
        # Add image name to metadata
        image_metadata.set_name(key)

        # Set the timestamp
        image_metadata.set_timestamp(value["timestamp"])

        # Get the GPS coordinates
        longitude = value["gps"].get_longitude()
        longitude_ref = value["gps"].get_longitude_ref()
        latitude = value["gps"].get_latitude()
        latitude_ref = value["gps"].get_latitude_ref()
        
        # Set the GPS coordinates
        image_metadata.set_coords(longitude, longitude_ref, latitude, latitude_ref)

        # Check to ensure the coordinates are in the correct format before processing
        if isinstance(latitude, tuple) and isinstance(longitude, tuple):
            try:
                # Convert the raw piexif tuple data to a decimal number accounting for ref
                decimal_latitude = convert_coord_to_decimal_number(latitude, latitude_ref)
                decimal_longitude = convert_coord_to_decimal_number(longitude, longitude_ref)
            except Exception as e:
                # Log the error
                main_logger.error(f"Error: Could not convert GPS coordinates to decimal for {key}: {e}")
                continue
            try:
                # Get the location from the GPS coordinates
                location = get_location_from_gps(decimal_latitude, decimal_longitude, image_dir)
                
                # Add location to metadata
                image_metadata.set_location(location)
                    
            except Exception as e:
                # Log the error
                main_logger.error(f"Error: Could not find location from GPS coordinates for {key}: {e}")
                continue
        else:
            # Log the error
            main_logger.error(f"Error: Invalid GPS coordinates for {key}")
            continue

    return image_metadata