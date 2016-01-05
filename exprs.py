from collections import ChainMap
from context import LispError

class LispVal:
    def __init__(self, val):
        self.val = val

    def children(self):
        return []

    def eval(self):
        return self

    def __bool__(self):
        return bool(self.val)

    def __repr__(self):
        return '{}({!r})'.format(self.__class__.__name__, self.val)

class LispSymbol(LispVal):
    def eval(self, env):
        return env[self.val]

class LispList(LispVal):
    def eval(self, env):
        if self:
            f = env.eval(self.val[0])
            if not callable(f):
                raise LispError('non-callable value in application')
            return f(self.val[1:], env)
        else:
            return self

    def children(self):
        return self.val

class LispFunc:
    def __init__(self, pars, body, name='anonymous function', clos=ChainMap()):
        self.pars, self.body, self.name, self.clos =\
                pars, body, name, clos

    def __call__(self, args, env):
        if len(args) != len(self.pars):
            raise LispError('wrong number of args given to {}'.format(self.name))
        args_ = map(env.eval, args)
        arg_scope = dict(zip(self.pars, args_))
        with env.scopes_as(self.clos), env.new_scope(arg_scope):
            return env.eval(self.body)

    def __repr__(self):
        return 'LispFunc({!r}, {!r}, {!r})'.\
                format(self.pars, self.body, self.name)

