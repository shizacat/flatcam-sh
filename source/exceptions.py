"""Project-wide exception types."""


class FlatCAMError(Exception):
    """Base exception for FlatCAM errors."""


class SettingsError(FlatCAMError):
    """Raised when application settings cannot be read or validated."""
