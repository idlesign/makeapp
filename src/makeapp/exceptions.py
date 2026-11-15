

class MakeappException(Exception):
    """Base makeapp exception."""


class AppMakerException(MakeappException):
    """Basic AppMaker related exception."""


class ProjectorException(MakeappException):
    """Basic Projector related exception."""


ProjectorExeption = ProjectorException
"""Deprecated alias for ProjectorException."""


class CommandError(MakeappException):
    """Raised when projector detects external process invocation error."""
