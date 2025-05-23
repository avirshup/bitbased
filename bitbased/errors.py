import typing as t


class BitBasedError(Exception):
    pass


class BitstringError(BitBasedError):
    pass


class LengthError(ValueError, BitstringError):
    """For problems relating to the length"""


class UnhandledValueError(NotImplementedError, BitstringError):
    """AKA "No. We don't do that here." """
