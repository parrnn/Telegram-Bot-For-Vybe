import re
def is_valid_range(r: str) -> bool:
    """
    Check if the given range string is valid (e.g., '1h', '7d').

    Args:
        r (str): Range string to validate.

    Returns:
        bool: True if valid, False otherwise.
    """
    return bool(re.fullmatch(r"\d+(h|d)", r))

def is_valid_address(address: str) -> bool:
    """
    Validate if the provided address is alphanumeric and 42 to 46 characters long.

    Args:
        address (str): Wallet or program address.

    Returns:
        bool: True if valid, False otherwise.
    """
    return bool(re.fullmatch(r"[a-zA-Z0-9]{42,46}", address))

def is_valid_limit(value: str) -> bool:
    """
    Validate if the input value is a positive integer.

    Args:
        value (str): Value to validate.

    Returns:
        bool: True if valid positive integer, False otherwise.
    """
    return value.isdigit() and int(value) > 0

def is_valid_days(value: str) -> bool:
    """
    Check if the number of days is between 1 and 30.

    Args:
        value (str): Days value as a string.

    Returns:
        bool: True if between 1 and 30, False otherwise.
    """
    return value.isdigit() and 1 <= int(value) <= 30

def is_valid_mint(address: str) -> bool:
    """
    Validate if the given mint address is alphanumeric and between 42-46 characters.

    Args:
        address (str): Mint address to validate.

    Returns:
        bool: True if valid, False otherwise.
    """
    return bool(re.fullmatch(r"[a-zA-Z0-9]{42,46}", address))

def is_valid_resolution(res: str) -> bool:
    """
    Validate if the resolution string is one of the allowed formats.

    Args:
        res (str): Resolution string (e.g., '1h', '1d', '1mo').

    Returns:
        bool: True if valid, False otherwise.
    """
    return bool(re.fullmatch(r"\d+(s|m|h|d|w|mo|y)", res))