# Standard Library imports
import piexif
import os

# Module imports
from src.utils.classes.ImageGPS import ImageGPS
from src.utils.set_logger import set_logger


def get_image_coords(image_dir):
    """
        Reads the GPS information from all images in the image directory and returns a dictionary.
        The dictionary has the filename as the key and the value is another dictionary containing the GPS information.
        The GPS information dictionary contains the latitude, longitude, and altitude of the image.
        If there is no GPS information found for an image, a message will be printed.
        If there is an error reading the image, a message will be printed.

        Following this documentation: https://piexif.readthedocs.io/en/latest/functions.html
    """

    # Initialize logger
    main_logger = set_logger(name="main", logfilename="main.log", log_path=image_dir, mode="a")
    

    coords = []
    
    for filename in os.listdir(image_dir):
        if filename.lower().endswith((".jpg", ".jpeg", ".webp", ".tiff", ".tif")):
            image_path = os.path.join(image_dir, filename)
            try:
                # Use piexif.load() with the file path directly
                exif_dict = piexif.load(image_path)

                if exif_dict:
                    gps_info = exif_dict.get("GPS", {})

                    # Get the GPS information using the piexif library constants for the GPS tags
                    latitude = gps_info.get(piexif.GPSIFD.GPSLatitude, None)
                    longitude = gps_info.get(piexif.GPSIFD.GPSLongitude, None)
                    
                    # Retrieve cardinal direction references
                    latitude_ref = gps_info.get(piexif.GPSIFD.GPSLatitudeRef, None)
                    longitude_ref = gps_info.get(piexif.GPSIFD.GPSLongitudeRef, None)

                    if latitude and longitude:
                        # Create an instance of the ImageGPS class
                        coords.append(
                            {
                                filename: ImageGPS(
                                    latitude=latitude,
                                    latitude_ref=latitude_ref,
                                    longitude=longitude,
                                    longitude_ref=longitude_ref
                                )
                            }
                        )
                    else:
                        # Log that no GPS information was found
                        try:
                            main_logger.info(f"No GPS information found for {filename}")
                        except Exception as e:
                            print(f"Error logging GPS information for {filename}: {e}")
                            
            except Exception as e:
                print(f"Error reading image {filename}: {e}")

    return coords