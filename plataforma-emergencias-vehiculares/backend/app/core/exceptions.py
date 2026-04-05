class AppException(Exception):
    """Excepción base de la aplicación."""

    def __init__(self, message: str = "Error en la aplicación") -> None:
        self.message = message
        super().__init__(self.message)


class NotFoundError(AppException):
    pass


class ConflictError(AppException):
    pass


class UnauthorizedError(AppException):
    pass


class ForbiddenError(AppException):
    pass
