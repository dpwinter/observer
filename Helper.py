import time, datetime

def map(value, orig_min, orig_max, new_min, new_max):
    """
    Function to interpolate between two ranges.
    
    value between orig_min and orig_max (orig_range) becomes new_value between new_min and new_max (new_range),
    that's in the same relation as value to the original range.
    """

    orig_range = orig_max - orig_min
    new_range  = new_max - new_min
    scaled_value = float(value - orig_min) / float(orig_range)
    return new_min + (scaled_value * new_range)

def get_timestamp():
    """Function to return timestamp in format YYYY-MM-DD_HH-MM-SS."""

    return datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H-%M-%S')
