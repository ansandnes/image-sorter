# Standard Library imports
import argparse
import time
import os
import logging
from pathlib import Path

# Module imports
from src.core.get_image_dir import get_image_dir
from src.utils.set_logger import set_logger
from src.utils.get_image_coords import get_image_coords
from src.core.create_image_metadata import create_image_metadata
from src.core.organize_images import organize_images
from src.core.processing_state import (
    initialize_processing_state,
    compute_file_hash,
    is_hash_processed,
    record_processed_image,
)
from src.utils.image_dir_path import image_dir as configured_image_dir


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(description="Sort images by location and date metadata.")
    parser.add_argument(
        "--image-dir",
        default=configured_image_dir,
        help="Path to image directory. Defaults to src/utils/image_dir_path.py value.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview planned moves without moving files or recording state.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set log verbosity level.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Shortcut for --log-level DEBUG.",
    )
    return parser.parse_args()


def main():

    # Global Timer
    start_time = time.time()

    # Parse args and read image directory from argument or project config
    args = parse_args()
    image_dir = args.image_dir
    log_level_name = "DEBUG" if args.verbose else args.log_level
    log_level = getattr(logging, log_level_name)

    # get image directory and check if it is valid.
    image_dir = get_image_dir(image_dir)

    if not image_dir:
        print(f"Invalid image directory: {configured_image_dir}")
        return

    # Initialize logger
    main_logger = set_logger(
        name="main",
        logfilename="main.log",
        log_path=image_dir,
        mode="w",
        level=log_level,
    )
    main_logger.info(f"Image directory: {image_dir}")
    main_logger.info(f"Dry run mode: {args.dry_run}")
    main_logger.info(f"Log level: {log_level_name}")
    db_path = initialize_processing_state(image_dir)
    main_logger.info(f"State database initialized at: {db_path}")

    # Loop through all images in the image directory
    for filename in os.listdir(image_dir):
        if filename.lower().endswith((".jpg", ".jpeg", ".webp", ".tiff", ".tif")):
            source_path = Path(image_dir) / filename

            try:
                file_hash = compute_file_hash(str(source_path))
            except Exception as error:
                main_logger.error(f"Failed to hash {filename}: {error}")
                continue

            if is_hash_processed(db_path, file_hash):
                main_logger.info(f"Skipping already processed image: {filename}")
                continue
    
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
            
            # Organize images based on location and sort by timestamp
            destination_path = organize_images(
                image_dir=image_dir,
                image_metadata=image_metadata,
                filename=filename,
                dry_run=args.dry_run,
            )
            if destination_path and not args.dry_run:
                record_processed_image(
                    db_path=db_path,
                    file_hash=file_hash,
                    original_path=str(source_path),
                    destination_path=destination_path,
                )
            elif destination_path and args.dry_run:
                main_logger.info(f"[DRY RUN] Skipping database write for {filename}")
            else:
                main_logger.error(f"Failed to organize {filename}; not recorded in state database.")


            #todo: Store metadata in database
            
            


    # Global Timer
    end_time = time.time()
    print("Total time taken: ", end_time - start_time, "seconds.")

if __name__ == "__main__":
    main()