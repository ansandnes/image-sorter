# Module imports
from src.utils.classes.Location import Location
from src.utils.set_logger import set_logger

# Third party imports
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

def get_location_from_gps(lat, lon, image_dir):
    """
        Get the location from a GPS coordinate.

        Args:
            lat: The latitude of the GPS coordinate.
            lon: The longitude of the GPS coordinate.

        Returns:
            dict: A dictionary containing the location details.
                The dictionary is in the format: {"location": {"country": country, "city": city}}
                If there is an error or the location is not found, None is returned.

        Raises:
            Exception: If there is an error finding the location from the GPS coordinates.
    """

    # Initialize logger
    main_logger = set_logger(name="main", log_path=image_dir, logfilename="main.log", mode="a")

    # Create a Nominatim geocoder
    loc = Nominatim(user_agent="GetLoc", timeout=10)
    
    try:
        # RateLimiter helps respect the Nominatim usage policy
        # by adding a delay between requests.
        reverse_geocoder = RateLimiter(loc.reverse, min_delay_seconds=1)
        
        # Find the location
        locname = reverse_geocoder(f"{lat}, {lon}", language="en")
        
        # Get the country and city
        address_details = locname.raw.get("address", {})
        country = address_details.get("country", "Unknown Country")  # Default to "Unknown Country"
        city = address_details.get("city", address_details.get("town", address_details.get("village", "Unknown City")))  # Default to "Unknown City"
        
        # Create a Location object containing the country and city
        location = Location()
        location.set_location(country, city)

    except Exception as e:
        # Create a Location object containing the country and city
        location = Location()
        country = "Unknown Country"
        city = "Unknown City"
        location.set_location(country, city)

        # Log the error
        main_logger.error(f"Error in get_location_from_gps.py: Could not find location from GPS coordinates: {e}")
    
    return location