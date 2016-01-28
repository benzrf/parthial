from collections import ChainMap
from .errs import LispNameError, UncallableError, ArgCountError

class LispVal:
    type_name = 'value'

    def __init__(self, val):
        self.val = val

    def children(self):
        return []

    def eval(self):
        return self

    def __bool__(self):
        return bool(self.val)

    def __str__(self):
        return str(self.val)

    def __repr__(self):
        return '{}({!r})'.format(self.__class__.__name__, self.val)

class LispSymbol(LispVal):
    type_name = 'symbol'
    FALSES = ['', 'false', 'no', 'off', '0', 'null', 'undefined', 'nan']

    def eval(self, env):
        if self.val in env:
            return env[self.val]
        else:
            raise LispNameError(self.val)

    def __bool__(self):
        return self.val.lower() not in self.FALSES

    def __str__(self):
        return repr(self.val)

class LispList(LispVal):
    type_name = 'list'

    def eval(self, env):
        if self:
            f = env.eval(self.val[0])
            if not callable(f):
                raise UncallableError(f)
            args = self.val[1:]
            if not f.quotes:
                args = list(map(env.eval, args))
            return f(env, args)
        else:
            return self

    def children(self):
        return self.val

    def __str__(self):
        return '(' + ' '.join(map(str, self.val)) + ')'

class LispFunc(LispVal):
    type_name = 'function'
    quotes = False

    def __init__(self, pars, body, name='anonymous function', clos=ChainMap()):
        self.pars, self.body, self.name, self.clos =\
                pars, body, name, clos

    def children(self):
        return [self.body] + list(self.clos.values())

    def __call__(self, env, args):
        if len(args) != len(self.pars):
            raise ArgCountError(self, len(args))
        arg_scope = dict(zip(self.pars, args))
        with env.scopes_as(self.clos), env.new_scope(arg_scope):
            return env.eval(self.body)

    def __bool__(self):
        return True

    def __str__(self):
        if self.name != 'anonymous function':
            return self.name
        else:
            pars = LispList(list(map(LispSymbol, self.pars)))
            return str(LispList([LispSymbol('lambda'), pars, self.body]))

    def __repr__(self):
        return 'LispFunc({!r}, {!r}, {!r})'.\
                format(self.pars, self.body, self.name)

class LispBuiltin(LispVal):
    type_name = 'builtin'

    def __init__(self, val, name, quotes=False):
        self.val, self.name, self.quotes = val, name, quotes

    def __call__(self, *args, **kwargs):
        return self.val(self, *args, **kwargs)

    def __str__(self):
        return self.name

