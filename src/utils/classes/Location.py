class Location:
    """
    A resolved place: country and city names, plus the IANA timezone of the
    city (for example "Europe/Oslo") when known.
    """
    def __init__(self, country: str, city: str, timezone: str | None = None):
        self.country: str = country
        self.city: str = city
        self.timezone: str | None = timezone

    def get_location(self):
        location: dict = {"location": {"country": self.country, "city": self.city}}
        return location

    def get_country(self):
        return self.country

    def get_city(self):
        return self.city

    def get_timezone(self):
        return self.timezone

    def __repr__(self) -> str:
        return f"Location({self.country!r}, {self.city!r})"
