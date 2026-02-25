class ModelConfigurationError(Exception):
    """Raised if the model has an invalid configuration."""
    def __init__(self):
        super().__init__()

class FatalConfigurationError(Exception):
    """Raised if the model has an invalid configuration and no way to function."""
    def __init__(self, message):
        super().__init__(message)
