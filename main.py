# Module imports
from src.utils.get_image_coords import get_image_coords
from src.utils.get_location_from_gps import get_location_from_gps
from src.utils.convert_coord_to_decimal_number import convert_coord_to_decimal_number
from src.utils.image_dir_path import image_dir

def main():

    # Create a dictionary to store image metadata
    image_metadata = {}

    # Get image GPS coordinates
    image_gps_coords = get_image_coords(image_dir)

    # Use the GPS details of each image to find the location
    for image in image_gps_coords.items():
        longitude = image[1]["longitude"]
        latitude = image[1]["latitude"]
        altitude = image[1]["altitude"]
        
        gps = {"gps": {
            "longitude": longitude,
            "latitude": latitude,
            "altitude": altitude
        }}

        # Add the GPS coordinates to the image metadata dictionary
        image_metadata[image[0]] = gps
        
        # Check to ensure the coordinates are in the correct format before processing
        if isinstance(latitude, tuple) and isinstance(longitude, tuple):
            try:
                # Convert the raw piexif tuple data to a decimal number
                decimal_latitude = convert_coord_to_decimal_number(latitude)
                decimal_longitude = convert_coord_to_decimal_number(longitude)
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
        
    print("image_metadata\n", image_metadata, "\n")
        


if __name__ == "__main__":
    main()