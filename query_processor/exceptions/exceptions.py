class AuthError(Exception):
    """Raised if there are authentication-related errors."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
