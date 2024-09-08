class BClientException(BaseException):
    """Базовый класс исключегий."""

class Unauthorized(BClientException):
    """Класс исключение, если был указан недействительный sessionid"""
