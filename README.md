# image-sorter

I have plenty of images on my hard drive that I have taken over the years. All of these images are stored in the same place. Many modern images contain rich metadata (EXIF data) that includes GPS coordinates and exact timestamps. This project aims to sort images by the time and location where the picture was taken. Corresponding folders will be created, and the photos will be reorganized.

As a User, I need a simple tool that scans a designated folder, extracts the location and time data from images, and automatically sorts them into a hierarchical folder structure based on Time and Location.


#### If you clone this repo, edit the image_dir variable in image_dir_path here:
    **src/utils/image_dir_path.py**


### Goals:

    **1. Metadata Extraction:** Efficiently read and parse EXIF data from every image file, specifically extracting the GPS coordinates and the Capture Timestamp.

    **2. Geocoding:** Convert the raw GPS coordinates (Latitude/Longitude) into a human-readable City and Country/Region name.

    **3. Classification & Tracking:** Store a persistent record of the image's original location, its extracted data, and its new, intended file path.

    **4. Idempotent Operation:** The system must be able to re-scan the folder without reprocessing or moving images that have already been classified and organized.


Idea:
    Store image metadata in a postgres db and use it to track my travels.

 ![alt text](image.png)
 