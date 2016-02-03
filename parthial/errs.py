"""
This module defines a hierarchy of exceptions that may be raised by the
interpreter.
"""

class LispError(Exception):
    """Base class for interpreter errors."""

    template = '{}'
    """A template for use in generating error messages."""

    def __init__(self, val):
        self.val = val

    def message(self):
        """Return a user-readable description of the error."""
        return self.template.format(self.val)

class LimitationError(LispError):
    """Expression violated evaluation limitations."""

class LispNameError(LispError):
    """Nonexistent variable."""

    template = 'nonexistent variable {!r}'

class LispTypeError(LispError):
    """Operation is undefined on given value's type."""

    def __init__(self, val, ex):
        self.val, self.ex = val, ex

    def message(self):
        ex = self.ex
        if isinstance(ex, type):
            ex = ex.type_name
        return 'expected {}, got the {} {}'.\
            format(ex, self.val.type_name, self.val)

class LispArgTypeError(LispTypeError):
    """Argument is of the wrong type."""

    def __init__(self, f, val, ex, arg):
        self.f, self.val, self.ex, self.arg = f, val, ex, arg

    def message(self):
        return 'in argument {} to {}: {}'.\
            format(self.arg, self.f, super().message())

class UncallableError(LispTypeError):
    """Applied value is uncallable."""

    def __init__(self, val):
        self.val = val
        self.ex = 'a callable'

class ArgCountError(LispTypeError):
    """Wrong number of args."""

    def __init__(self, f, got, ex=None):
        if not ex:
            ex = len(f.pars)
        self.f, self.ex, self.got = f, ex, got

    def message(self):
        return 'wrong number of args given to {}: expected {}, got {}'.\
            format(self.f, self.ex, self.got)

