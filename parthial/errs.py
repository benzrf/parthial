class LispError(Exception):
    template = '{}'

    def __init__(self, val):
        self.val = val

    def message(self):
        return self.template.format(self.val)

class LimitationError(LispError):
    pass

class LispNameError(LispError):
    template = 'nonexistent variable {!r}'

class LispTypeError(LispError):
    def __init__(self, val, ex):
        self.val, self.ex = val, ex

    def message(self):
        ex = self.ex
        if isinstance(ex, type):
            ex = ex.type_name
        return 'expected {}, got the {} {}'.\
            format(ex, self.val.type_name, self.val)

class LispArgTypeError(LispTypeError):
    def __init__(self, f, val, ex, arg):
        self.f, self.val, self.ex, self.arg = f, val, ex, arg

    def message(self):
        return 'in argument {} to {}: {}'.\
            format(self.arg, self.f, super().message())

class UncallableError(LispTypeError):
    def __init__(self, val):
        self.val = val
        self.ex = 'a callable'

class ArgCountError(LispTypeError):
    def __init__(self, f, got, ex=None):
        if not ex:
            ex = len(f.pars)
        self.f, self.ex, self.got = f, ex, got

    def message(self):
        return 'wrong number of args given to {}: expected {}, got {}'.\
            format(self.f, self.ex, self.got)

