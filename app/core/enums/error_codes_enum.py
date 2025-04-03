from enum import Enum


class ErrorCodes(Enum):
    """
    Standardized error codes for HTTP responses and custom application errors.

    - 1xx, 2xx, 3xx: Standard HTTP status codes.
    - 4xx: Client errors (Bad Requests, Unauthorized, Not Found, etc.).
    - 5xx: Server errors (Internal Server Errors, Service Unavailable, etc.).
    - 10xx - 15xx: Custom application-specific error codes for debugging and tracking.
    """

    # ✅ 2xx - Success Responses
    SUCCESS = 200  # Request was successful (e.g., fetching data)
    CREATED = 201  # Resource was created successfully (e.g., user registered)
    NO_CONTENT = 204  # Request processed, but no content to return

    # ❌ 4xx - Client Errors (User/Client Mistakes)
    BAD_REQUEST = 400  # Invalid request (e.g., missing fields, bad JSON)
    UNAUTHORIZED = 401  # User is not authenticated (e.g., missing/invalid token)
    FORBIDDEN = 403  # User authenticated but not allowed (e.g., role-based access)
    NOT_FOUND = 404  # Resource not found (e.g., user ID doesn't exist)
    CONFLICT = 409  # Conflict in request (e.g., trying to create duplicate resource)
    UNPROCESSABLE_ENTITY = 422  # Validation failed (e.g., invalid email format)
    TOO_MANY_REQUESTS = 429  # Rate limiting exceeded (e.g., spam requests)

    # 🚨 5xx - Server Errors (Backend/Database Issues)
    INTERNAL_SERVER_ERROR = 500  # Generic server error (unexpected failure)
    SERVICE_UNAVAILABLE = 503  # Server is temporarily down
    GATEWAY_TIMEOUT = 504  # API request took too long (network issue)
    CONNECTION_ERROR = 520  # Unable to connect to external services
    SERVER_OVERLOADED = 530  # Server is too busy to handle requests
    MAINTENANCE_MODE = 531  # API is down for scheduled maintenance

    # 🔹 10xx - Generic Application Errors
    GENERIC_ERROR = 1000  # General error for unexpected issues
    DATABASE_ERROR = 1001  # Database connection issue (e.g., can't reach DB)
    QUERY_ERROR = 1002  # SQLAlchemy or query-related issues
    CACHE_ERROR = 1003  # Issues with cache layer (e.g., Redis failure)

    # 🔑 11xx - Authentication & Authorization Errors
    AUTH_FAILED = 1100  # Authentication failed (e.g., invalid credentials)
    INVALID_API_KEY = 1101  # API Key is invalid
    UNAUTHORIZED_ACCESS = 1102  # User lacks required role

    # 📥 12xx - Input Validation Errors
    MISSING_PARAMETERS = 1200  # Required parameters missing in request
    INVALID_FORMAT = 1201  # Data provided is malformed (e.g., invalid date format)

    # 🚧 13xx - Rate Limiting & Abuse Prevention
    RATE_LIMIT_EXCEEDED = 1300  # User exceeded allowed requests per timeframe

    # 🌐 14xx - Third-Party Service Issues
    THIRD_PARTY_SERVICE_ERROR = 1400  # Error from an external API (e.g., Stripe, AWS)

    # ⏳ 15xx - Background Jobs / Async Processing Issues
    BACKGROUND_JOB_FAILED = 1500  # Celery or async job failed

    def __str__(self):
        """Returns the integer value of the Enum."""
        return str(self.value)
