# Standard Library imports
import time
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

    #---<>
    # get image directory and check if it is valid. Log if validated.
    
    # Start timing get_image_dir
    start_time_get_image_dir = time.time()

    image_dir = get_image_dir(image_dir)

    # Stop timing get_image_dir
    end_time_get_image_dir = time.time()
    print("Time taken to get image directory: ", end_time_get_image_dir - start_time_get_image_dir, "seconds.")
    #---</>
    
    #---<>
    # Get image GPS coordinates and timestamps
    
    # Start timing get_image_coords
    start_time_get_image_coords = time.time()
    
    list_of_image_gps_dicts = get_image_coords(image_dir)

    # Stop timing get_image_coords
    end_time_get_image_coords = time.time()
    print("Time taken to get image coordinates: ", end_time_get_image_coords - start_time_get_image_coords, "seconds.")
    #---</>
    
    #---<>
    # Create image metadata

    # Start timing create_image_metadata
    start_time_create_image_metadata = time.time()

    for image_gps_dict in list_of_image_gps_dicts:
        image_metadata = create_image_metadata(image_gps_dict, image_dir)

        # # Print image metadata
        # print("main_oop:\n", image_metadata, "\n")
        # print("main_oop:\n", image_metadata.get_name(), "\n")
        # print("main_oop:\n", image_metadata.get_timestamp(), "\n")
        # print("main_oop:\n", image_metadata.get_coords().get_latitude(), "\n")
        # print("main_oop:\n", image_metadata.get_location().get_country(), "\n")
        # print("main_oop:\n", image_metadata.get_location().get_city(), "\n")
        

    # Stop timing create_image_metadata
    end_time_create_image_metadata = time.time()
    print("Time taken to create image metadata: ", end_time_create_image_metadata - start_time_create_image_metadata, "seconds.")
    #---</>


    #todo: Organize images

    
    #todo: Create database


    # Global Timer
    end_time = time.time()
    print("Total time taken: ", end_time - start_time, "seconds.")

if __name__ == "__main__":
    main()