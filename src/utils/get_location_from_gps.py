from geopy.geocoders import Nominatim
import json
from geopy.extra.rate_limiter import RateLimiter

def get_location_from_gps(lat:float, lon:float) -> dict:
    """
        Get the location from a GPS coordinate.

        Args:
            lat (float): The latitude of the GPS coordinate.
            lon (float): The longitude of the GPS coordinate.

        Returns:
            dict: A dictionary containing the location details.
                The dictionary is in the format: {"location": {"country": country, "city": city}}
                If there is an error or the location is not found, None is returned.

        Raises:
            Exception: If there is an error finding the location from the GPS coordinates.
    """

    # Create a dictionary to store the location details
    location_dict = {}

    # Create a Nominatim geocoder
    loc = Nominatim(user_agent="GetLoc", timeout=10)
    
    try:
        # RateLimiter helps respect the Nominatim usage policy
        # by adding a delay between requests.
        reverse_geocoder = RateLimiter(loc.reverse, min_delay_seconds=1)
        locname = reverse_geocoder(f"{lat}, {lon}", language="en")
        
        if locname:
            address_details = locname.raw.get("address", {})
            country = address_details.get("country", "Unknown Country")
            city = address_details.get("city", address_details.get("town", address_details.get("village", "Unknown City")))
            
            location_dict = {"location": {"country": country, "city": city}}
        else:
            print("Location not found or invalid response.")
    except Exception as e:
        print(f"Error: Could not find location from GPS coordinates: {e}")
    
    return location_dict