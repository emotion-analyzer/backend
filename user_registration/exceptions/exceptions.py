class UserAlreadyExistsError(Exception):
    def __init__(self, field: str):
        self.field = field
        self.message = f"Usuario ya registrado con este {field}."
        super().__init__(self.message)


class AuthError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
