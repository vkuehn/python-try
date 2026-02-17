"""Example module demonstrating Google-style docstrings.

This module contains example functions with proper Google-style docstring
formatting, type hints, and testing setup.

Todo:
    * Add more example functions
    * Add class examples
    * Add exception handling examples

Note:
    This module follows Google Python Style Guide:
    https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings
"""


def main(hello: str) -> str:
    """Demonstrates proper Google-style function docstrings.

    This function shows various sections that can be used in Google-style
    docstrings, including extended description, args, returns, raises,
    examples, and notes.

    Args:
        hello (str): Input string to be processed. Can be any non-empty string.

    Returns:
        str: A formatted string containing the input parameter.

    Raises:
        ValueError: If bar is an empty string.

    Examples:
        >>> foo("hello")
        'foo received hello'
        >>> foo("world")
        'foo received world'

    Note:
        This is a simple example function used primarily for demonstration.
        In real-world applications, more complex processing might occur.

    Attributes:
        __author__ (str): Function author's name
        __version__ (str): Current version of the function
    """
    return f"main received {hello}"


if __name__ == "__main__":  # pragma: no cover
    main("world")
