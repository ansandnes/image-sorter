# Module imports
from src.core.create_image_metadata import create_image_metadata
from src.utils.image_dir_path import image_dir

def main():

    # Call the function to create image metadata
    create_image_metadata(image_dir)
        


if __name__ == "__main__":
    main()