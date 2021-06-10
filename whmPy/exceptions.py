"""
Exceptions
"""


class WhmPyException(Exception):
    """
    Basically creating a namespace for exceptions
    """
    pass


class SortedFieldNotDisplayed(WhmPyException):
    """
    A column that was specified as part of a sort isn't set to be displayed
    """
    pass
