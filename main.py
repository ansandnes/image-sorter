# Standard Library imports
import time
import os

from pprint import pprint

# Module imports
from src.core.get_image_dir import get_image_dir
from src.utils.get_image_coords import get_image_coords
from src.core.create_image_metadata import create_image_metadata


def main():

    # Global Timer
    start_time = time.time()

    # Prompt user for the path of the image directory
    # image_dir = input("Enter the path of the image directory: ")
    image_dir = "assets/images/test_images"

    # get image directory and check if it is valid. Log if validated.
    image_dir = get_image_dir(image_dir)

    # Loop through all images in the image directory
    for filename in os.listdir(image_dir):
        if filename.lower().endswith((".jpg", ".jpeg", ".webp", ".tiff", ".tif")):
    
            # Get image GPS coordinates and timestamp
            timestamp, coords = get_image_coords(image_dir, filename)
    
            # Create image metadata
            image_metadata = create_image_metadata(timestamp, coords, image_dir, filename)
                
            # # Print image metadata
            # print("main:\n", image_metadata, "\n")
            # print("name:\n", image_metadata.get_name(), "\n")
            # print("timestamp:\n", image_metadata.get_timestamp(), "\n")
            
            # print("coords:\n", image_metadata.get_coords(), "\n")
            # print("latitude:\n", image_metadata.get_coords().get_latitude(), "\n")
            # print("latitude_ref:\n", image_metadata.get_coords().get_latitude_ref(), "\n")
            # print("longitude:\n", image_metadata.get_coords().get_longitude(), "\n")
            # print("longitude_ref:\n", image_metadata.get_coords().get_longitude_ref(), "\n")

            # print("location:\n", image_metadata.get_location(), "\n")
            # print("country:\n", image_metadata.get_location().get_country(), "\n")
            # print("city:\n", image_metadata.get_location().get_city(), "\n")
            

            #todo: Create database

    #todo: Organize images

    
    


    # Global Timer
    end_time = time.time()
    print("Total time taken: ", end_time - start_time, "seconds.")

if __name__ == "__main__":
    main()