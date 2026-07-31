"""Custom exceptions for MOSS Partner SDK."""

from __future__ import annotations


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
        code: str | None = None,
        response_body: str | None = None,
    ):
        self.status_code = status_code
        self.code = code or "unknown_error"
        self.response_body = response_body
        super().__init__(message)

    def __str__(self) -> str:
        return f"API Error {self.status_code} ({self.code}): {self.message}"


class MossNetworkError(MossError):
    """Exception raised when network request fails."""



class MossValidationError(MossError):
    """Exception raised when input validation fails."""



class MossParseError(MossError):
    """Exception raised when response parsing fails."""

