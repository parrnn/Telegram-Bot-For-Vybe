from datetime import timezone, datetime
from typing import Union

def format_number_human_readable(num: Union[int, float]) -> str:
    """
    Convert a large number into a human-readable format (e.g., 1.2K, 3.4M).

    Args:
        num (int or float): Number to format.

    Returns:
        str: Human-readable string representation.
    """
    try:
        num = float(num)
        for unit in ["", "K", "M", "B", "T"]:
            if abs(num) < 1000.0:
                return f"{num:.2f}{unit}"
            num /= 1000.0
        return f"{num:.2f}P"
    except (ValueError, TypeError):
        return "N/A"

def full_datetime_to_unix(human_time_str: str) -> Union[int, None]:
    """
    Convert a date string (YYYY-MM-DD) into a Unix timestamp in UTC.

    Args:
        human_time_str (str): Date string in 'YYYY-MM-DD' format.

    Returns:
        int | None: Unix timestamp if valid, otherwise None.
    """
    try:
        dt = datetime.strptime(human_time_str, '%Y-%m-%d')
        return int(dt.replace(tzinfo=timezone.utc).timestamp())
    except ValueError:
        return None

def timestamp_to_date(timestamp: int) -> str:
    """
    Convert a Unix timestamp to a human-readable date string (UTC).

    Args:
        timestamp (int): Unix timestamp.

    Returns:
        str: Date string in 'YYYY-MM-DD HH:MM' format.
    """
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M')