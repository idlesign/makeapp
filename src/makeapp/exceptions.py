

class MakeappException(Exception):
    """Base makeapp exception."""


class AppMakerException(MakeappException):
    """Basic AppMaker related exception."""


class ProjectorExeption(MakeappException):
    """Basic Projector related exception."""


class CommandError(MakeappException):
    """Raised when projector detects external process invocation error."""
