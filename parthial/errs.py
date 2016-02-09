"""
A hierarchy of exceptions that may be raised by the interpreter.
"""

class LispError(Exception):
    """Base class for interpreter errors.

    Attributes:
        template: A template for use in generating error messages.
        val: The primary value involved in the error.
    """

    template = '{}'

    def __init__(self, val):
        self.val = val

    def message(self):
        """
        Returns:
            A user-readable description of the error.
        """
        return self.template.format(self.val)

class LimitationError(LispError):
    """Expression violated evaluation limitations.

    Attributes:
        val (str): The error message.
    """

class LispNameError(LispError):
    """Nonexistent variable.

    Attributes:
        val (str): The name of the nonexistent variable.
    """

    template = 'nonexistent variable {!r}'

class LispTypeError(LispError):
    """Operation is undefined on given value's type.

    Attributes:
        val (LispVal): The given value.
        ex (type or str): The expected type.
    """

    def __init__(self, val, ex):
        self.val, self.ex = val, ex

    def message(self):
        ex = self.ex
        if isinstance(ex, type):
            ex = ex.type_name
        return 'expected {}, got the {} {}'.\
            format(ex, self.val.type_name, self.val)

class LispArgTypeError(LispTypeError):
    """Argument is of the wrong type.

    Attributes:
        f (callable): The function that was called.
        arg (int): The argument number.
    """

    def __init__(self, f, val, ex, arg):
        self.f, self.val, self.ex, self.arg = f, val, ex, arg

    def message(self):
        return 'in argument {} to {}: {}'.\
            format(self.arg, self.f, super().message())

class UncallableError(LispTypeError):
    """Applied value is uncallable.

    Attributes:
        val (LispVal): The value that was called.
    """

    def __init__(self, val):
        self.val = val
        self.ex = 'a callable'

class ArgCountError(LispTypeError):
    """Wrong number of args.

    Attributes:
        f (callable): The function that was called.
        got (int): The number of arguments given.
        ex (int): The expected number of arguments.
                  Defaults to ``len(f.pars)``.
    """

    def __init__(self, f, got, ex=None):
        if not ex:
            ex = len(f.pars)
        self.f, self.ex, self.got = f, ex, got

    def message(self):
        return 'wrong number of args given to {}: expected {}, got {}'.\
            format(self.f, self.ex, self.got)

