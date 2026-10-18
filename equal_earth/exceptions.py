"""Custom exceptions for the Equal Earth India mapping toolkit."""


class EqualEarthError(Exception):
    """Base exception for all Equal Earth toolkit errors."""
    pass


class ProjectionError(EqualEarthError):
    """Raised when coordinate transformation or projection math fails."""
    pass


class DataValidationError(EqualEarthError):
    """Raised when geographic dataset or input table fails validation."""
    pass


class RenderError(EqualEarthError):
    """Raised when map rendering or canvas layout fails."""
    pass


class ExportError(EqualEarthError):
    """Raised when file export (PNG, SVG, PDF) fails."""
    pass
