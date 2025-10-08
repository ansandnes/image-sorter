# Standard Library imports
from pprint import pprint

# Module imports
from src.core.get_image_dir import get_image_dir
# from src.utils.get_image_timestamp import get_image_timestamp
from src.utils.get_image_coords import get_image_coords
from src.core.create_image_metadata import create_image_metadata


def main():

    # Prompt user for the path of the image directory
    # image_dir = input("Enter the path of the image directory: ")
    image_dir = "assets/images/test_images"

    # get image directory and check if it is valid. Log if validated.
    image_dir = get_image_dir(image_dir)

    #todo:
    # # Get image timestamp
    # image_timestamp = get_image_timestamp(image_dir)

    # Get image GPS coordinates
    list_of_image_gps_objects = get_image_coords(image_dir)

    # Print image GPS coordinates
    # print("\n", "list_of_image_gps_objects:\n", list_of_image_gps_objects, "\n")

    for image_gps_object in list_of_image_gps_objects:
        image_metadata = create_image_metadata(image_gps_object, image_dir)

        # Print image metadata
        print("main_oop:\n", image_metadata, "\n")
        print("main_oop:\n", image_metadata.get_name(), "\n")
        print("main_oop:\n", image_metadata.get_coords().get_latitude(), "\n")
        print("main_oop:\n", image_metadata.get_location().get_country(), "\n")
        print("main_oop:\n", image_metadata.get_location().get_city(), "\n")
        




if __name__ == "__main__":
    main()