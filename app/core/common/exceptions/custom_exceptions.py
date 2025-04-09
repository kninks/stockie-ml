from app.core.enums.error_codes_enum import ErrorCodes


class CustomAPIError(Exception):
    def __init__(
        self, status_code: int, error_code: int, message: str = "An error occurred"
    ):
        self.status_code = status_code
        self.error_code = error_code
        self.message = message
        super().__init__(self.message)


class AuthError(CustomAPIError):
    def __init__(self, message="Authentication failed"):
        super().__init__(status_code=401, error_code=1100, message=message)


class ForbiddenError(CustomAPIError):
    def __init__(self, message="You do not have permission to access this resource"):
        super().__init__(status_code=403, error_code=1101, message=message)


class ResourceNotFoundError(CustomAPIError):
    def __init__(self, resource="Resource", message=None):
        super().__init__(
            status_code=404, error_code=1200, message=message or f"{resource} not found"
        )


class RateLimitExceededError(CustomAPIError):
    """Raised when a user exceeds allowed request limits."""

    def __init__(self, message="Too many requests"):
        super().__init__(status_code=429, error_code=1300, message=message)


class BackgroundJobError(CustomAPIError):
    """Raised when a background task fails."""

    def __init__(self, job_name="Background Job", message=None):
        super().__init__(
            status_code=500, error_code=1500, message=message or f"{job_name} failed"
        )


class BackendServerError(CustomAPIError):
    def __init__(self, message="Error contacting Stockie Backend server"):
        super().__init__(
            status_code=ErrorCodes.SERVICE_UNAVAILABLE.value,  # 503
            error_code=ErrorCodes.THIRD_PARTY_SERVICE_ERROR.value,  # 1400
            message=message,
        )
