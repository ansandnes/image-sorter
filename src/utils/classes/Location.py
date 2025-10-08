class Location:
    """  """
    def __init__(self):
        """  """
        self.country = None
        self.city = None

    def set_location(self, country, city):
        self.country = country
        self.city = city

    def get_location(self, country, city):
        location = {"location": {"country": country, "city": city}}
        return location
    
    def get_country(self):
        return self.country
    
    def get_city(self):
        return self.city
    