def convert_coord_to_decimal_number(coord: tuple, ref: bytes) -> float:
    """
    Converts a GPS coordinate from the raw format returned by the piexif
    library to a single decimal number.
    
    The coordinate tuple is in the format:
    ((degrees_num, degrees_den), (minutes_num, minutes_den), (seconds_num, seconds_den))
    
    Args:
        coord (tuple): A tuple containing the degrees, minutes, and seconds.
        ref (str): The cardinal direction reference ('N', 'S', 'E', or 'W').
    
    Returns:
        float: The coordinate converted to a decimal number.
    """
    # Calculate the decimal value from the tuple
    degrees = coord[0][0] / coord[0][1]
    minutes = coord[1][0] / coord[1][1]
    seconds = coord[2][0] / coord[2][1]

    decimal_coord = degrees + minutes / 60 + seconds / 3600

    # Apply the cardinal direction reference
    if ref.decode() in ['S', 'W']:
        return -decimal_coord
    else:
        return decimal_coord