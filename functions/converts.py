def to_float_safe(val, default: float = 0.0) -> float:
    """
    Safely convert a value to a float.

    Attempts to cast the input to a float. If the conversion fails
    due to a ValueError or TypeError, returns a provided default value.

    Args:
        val:
            The value to convert to float (can be any type).
        default (float, optional):
            Value to return if conversion fails. Defaults to 0.0.

    Returns:
        float:
            The successfully converted float value, or the default if conversion fails.

    Example:
        >>> to_float_safe("3.14")
        3.14
        >>> to_float_safe(None)
        0.0
        >>> to_float_safe("abc", default=1.0)
        1.0
    """
    try:
        return float(val)
    except (ValueError, TypeError):
        return default
