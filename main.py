# Standard Library imports
from pprint import pprint

# Module imports
from src.core.create_image_metadata import create_image_metadata
from src.utils.image_dir_path import image_dir

def main():
    
    # Call the function to create image metadata
    image_metadata = create_image_metadata(image_dir)
    
    # Print the image metadata
    pprint(image_metadata)



if __name__ == "__main__":
    main()