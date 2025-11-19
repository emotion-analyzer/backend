class UserAlreadyExistsError(Exception):
    """Raised if username/email already exist in the database."""

    def __init__(self, field: str):
        self.field = field
        self.message = f"Usuario ya registrado con este {field}."
        super().__init__(self.message)


class UserDoesntExistError(Exception):
    """Raised if user is not present in the database."""

    def __init__(self):
        self.message = "Usuario no encontrado."
        super().__init__(self.message)


class AuthError(Exception):
    """Raised if there are authentication-related errors."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class ImageFormatError(Exception):
    """Raised if image has invalid format."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class ExternalServiceConnectionError(Exception):
    """Raised if user is not present in the database."""

    def __init__(self, service: str):
        self.message = f"Conexion al servicio de {service} fallida"
        super().__init__(self.message)
