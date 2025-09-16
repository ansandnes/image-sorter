import piexif
import os

def get_image_coords(image_dir):
    """
        Reads the GPS information from all images in the image directory and returns a dictionary.
        The dictionary has the filename as the key and the value is another dictionary containing the GPS information.
        The GPS information dictionary contains the latitude, longitude and altitude of the image.
        If there is no GPS information found for an image, a message will be printed.
        If there is an error reading the image, a message will be printed.

        Following this documentation: https://piexif.readthedocs.io/en/latest/functions.html
    """
    coords = {}
    
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
                    altitude = gps_info.get(piexif.GPSIFD.GPSAltitude, None)
                    
                    if latitude and longitude:
                        coords[filename] = {
                            'latitude': latitude,
                            'longitude': longitude,
                            'altitude': altitude,
                        }
                    else:
                        print(f"No GPS information found in image {filename}")
                        coords[filename] = {
                            'latitude': "unknown",
                            'longitude': "unknown",
                            'altitude': "unknown",
                        }
            except Exception as e:
                print(f"Error reading image {filename}: {e}")

    return coords