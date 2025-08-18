"""
Custom exceptions for pico-report package.
"""


class PicoReportError(Exception):
    """Base exception for pico-report package."""
    pass


class PicoAuthError(PicoReportError):
    """Exception raised for authentication-related errors."""
    pass


class PicoUploadError(PicoReportError):
    """Exception raised for data upload errors."""
    pass


class PicoConfigError(PicoReportError):
    """Exception raised for configuration-related errors."""
    pass