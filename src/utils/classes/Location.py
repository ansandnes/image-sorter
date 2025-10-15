class Location:
    """  """
    def __init__(self, country: str, city: str):
        """  """
        self.country: str = country
        self.city: str = city

    def get_location(self):
        location: dict = {"location": {"country": self.country, "city": self.city}}
        return location
    
    def get_country(self):
        return self.country
    
    def get_city(self):
        return self.city
    