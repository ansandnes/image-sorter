# Module imports
from src.utils.classes.ImagePath import ImagePath
from src.utils.set_logger import set_logger


def get_image_dir(image_dir: str) -> str:
    """
        This function takes a string representing a path to an image directory,
        validates it, and returns the path to the directory after validation.
        If the path is invalid, the function prints an error message and returns an empty string.
        The function also initializes a logger with the name "main" and logs the path of the image directory.
    """

    # Create an instance of the ImagePath class
    image_path = ImagePath(image_dir)

    # Check if the path is valid
    if not ImagePath(image_dir).is_valid():
        print("Invalid path. Exiting.")
        return ""
    
    # Overwrite image_dir by the directory obtained by the ImagePath class
    image_dir = image_path.get_path()

    # Initialize logger
    main_logger = set_logger(name="main", logfilename="main.log", log_path=image_dir, mode="w")  

    # Log the path of the image directory
    main_logger.info(f"Image directory: {image_dir}")

    return image_dir