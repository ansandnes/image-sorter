# Module imports
from src.utils.classes.ImagePath import ImagePath


def get_image_dir(image_dir: str) -> str:
    """
        This function takes a string representing a path to an image directory,
        validates it, and returns the path to the directory after validation.
        If the path is invalid, the function logs an error message and returns an empty string.
        The function also initializes a logger with the name "main" and logs the path of the image directory.
        I do not yet see the necesesity for the ImagePath class. But I'm learning about oop so I'll leave it here for now.
    """

    # Create an instance of the ImagePath class
    image_path = ImagePath(image_dir)

    # Check if the path is valid
    if not image_path.is_valid():
        return ""
    
    # Overwrite image_dir by the directory obtained by the ImagePath class
    image_dir = image_path.get_path()

    return image_dir