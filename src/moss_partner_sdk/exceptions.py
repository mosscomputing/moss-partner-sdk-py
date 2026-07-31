"""Custom exceptions for MOSS Partner SDK."""

from typing import Optional


class MossError(Exception):
    """Base exception for all MOSS SDK errors."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class MossAPIError(MossError):
    """Exception raised when API returns an error response."""

    def __init__(
        self,
        message: str,
        status_code: int,
        code: Optional[str] = None,
        response_body: Optional[str] = None,
    ):
        self.status_code = status_code
        self.code = code or "unknown_error"
        self.response_body = response_body
        super().__init__(message)

    def __str__(self) -> str:
        return f"API Error {self.status_code} ({self.code}): {self.message}"


class MossNetworkError(MossError):
    """Exception raised when network request fails."""

    pass


class MossValidationError(MossError):
    """Exception raised when input validation fails."""

    pass


class MossParseError(MossError):
    """Exception raised when response parsing fails."""

    pass
