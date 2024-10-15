class BClientException(Exception):
    """Базовый класс исключегий."""

class InternalError(BClientException):
    """Класс исключений, вызываемых если сайт недоступен."""

class Unauthorized(BClientException):
    """Класс исключений, вызываемых если был указан недействительный sessionid"""
