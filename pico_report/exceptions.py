"""
Custom exceptions for pico-report package.
"""


class PicoReportError(Exception):
    """Base exception for pico-report errors."""
    pass


class PicoAuthError(PicoReportError):
    """Raised when authentication fails."""
    pass


class PicoUploadError(PicoReportError):
    """Raised when data upload fails."""
    pass


class PicoConfigError(PicoReportError):
    """Raised when configuration is invalid."""
    pass


class PicoGitError(PicoReportError):
    """Raised when git operations fail."""
    pass
