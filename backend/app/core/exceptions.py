"""Custom exception classes and error handlers."""
from fastapi import status


class InsightForgeException(Exception):
    """Base exception for InsightForge."""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class AuthenticationError(InsightForgeException):
    """Raised for authentication failures."""

    def __init__(self, message: str = "Invalid credentials"):
        super().__init__(message, status_code=status.HTTP_401_UNAUTHORIZED)


class AuthorizationError(InsightForgeException):
    """Raised for authorization failures."""

    def __init__(self, message: str = "Not authorized"):
        super().__init__(message, status_code=status.HTTP_403_FORBIDDEN)


class NotFoundError(InsightForgeException):
    """Raised when a resource is not found."""

    def __init__(self, resource: str = "Resource"):
        super().__init__(f"{resource} not found", status_code=status.HTTP_404_NOT_FOUND)


class ValidationError(InsightForgeException):
    """Raised for data validation failures."""

    def __init__(self, message: str = "Validation error"):
        super().__init__(message, status_code=422)


class FileUploadError(InsightForgeException):
    """Raised for file upload problems."""

    def __init__(self, message: str = "File upload error"):
        super().__init__(message, status_code=status.HTTP_400_BAD_REQUEST)
