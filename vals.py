from collections import ChainMap

class LispError(Exception):
    pass

class LispVal:
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
    FALSES = ['', 'false', 'no', 'off', '0', 'null', 'undefined', 'nan']

    def eval(self, env):
        if self.val in env:
            return env[self.val]
        else:
            raise LispError('nonexistent variable')

    def __bool__(self):
        return self.val.lower() not in self.FALSES

    def __str__(self):
        return repr(self.val)

class LispList(LispVal):
    def eval(self, env):
        if self:
            f = env.eval(self.val[0])
            if not callable(f):
                raise LispError('non-callable value in application')
            args = self.val[1:]
            if not f.quotes:
                args = list(map(env.eval, args))
            return f(args, env)
        else:
            return self

    def children(self):
        return self.val

    def __str__(self):
        return '(' + ' '.join(map(str, self.val)) + ')'

class LispFunc(LispVal):
    quotes = False

    def __init__(self, pars, body, name='anonymous function', clos=ChainMap()):
        self.pars, self.body, self.name, self.clos =\
                pars, body, name, clos

    def children(self):
        return [self.body] + list(self.clos.values())

    def __call__(self, args, env):
        if len(args) != len(self.pars):
            raise LispError('wrong number of args given to {}'.format(self.name))
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
    def __init__(self, val, name, quotes=False):
        self.val, self.name, self.quotes = val, name, quotes

    def __call__(self, *args, **kwargs):
        return self.val(*args, **kwargs)

    def __str__(self):
        return self.name

