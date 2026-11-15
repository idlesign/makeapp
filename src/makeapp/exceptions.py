

class MakeappException(Exception):
    """Base makeapp exception."""


class AppMakerException(MakeappException):
    """Basic AppMaker related exception."""


class ProjectorException(MakeappException):
    """Basic Projector related exception."""


class CommandError(MakeappException):
    """Raised when projector detects external process invocation error."""
