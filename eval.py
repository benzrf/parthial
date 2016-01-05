from contextlib import contextmanager
from collections import ChainMap
from weakref import WeakSet

# interpretation

class InterpreterError(Exception):
    pass

class LispError(Exception):
    pass

class EvalContext:
    def __init__(self, globals={}, max_depth=100, max_steps=10000, max_things=5000):
        self.scopes = ChainMap({}, globals)
        self.max_depth, self.max_steps, self.max_things =\
                max_depth, max_steps, max_things
        self.depth = self.steps = 0
        self.things = WeakSet()

    @contextmanager
    def scopes_as(self, new_scopes):
        old_scopes, self.scopes = self.scopes, new_scopes
        yield
        self.scopes = old_scopes

    @contextmanager
    def new_scope(self, new_scope={}):
        old_scopes, self.scopes = self.scopes, self.scopes.new_child(new_scope)
        yield
        self.scopes = old_scopes

    def eval(self, expr):
        if self.depth >= self.max_depth:
            raise InterpreterError('too much nesting')
        if self.steps >= self.max_steps:
            raise InterpreterError('too many steps')
        self.depth += 1
        self.steps += 1
        r = expr.eval(self)
        self.depth -= 1
        return r

    def new(self, val):
        if len(self.things) >= self.max_things:
            raise InterpreterError('too many things')
        self.things.add(val)
        return val

    def rec_new(self, val):
        for child in val.children():
            self.rec_new(child)
        self.new(val)

    def run(self, expr):
        self.rec_new(expr)
        res = self.eval(expr)
        return res, self.things

    def __getitem__(self, *args, **kwargs):
        return self.scopes.__getitem__(*args, **kwargs)

    def __setitem__(self, *args, **kwargs):
        return self.scopes.__setitem__(*args, **kwargs)

    def __hasitem__(self, k):
        return k in self.scopes

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

# builtins

def lisp_eval(args, env):
    args = list(map(env.eval, args))
    if len(args) != 1:
        raise LispError('wrong number of args given to eval')
    return env.eval(args[0])

def lisp_apply(args, env):
    args = list(map(env.eval, args))
    if len(args) != 2:
        raise LispError('wrong number of args given to apply')
    f, xs = args
    if not callable(f):
        raise LispError('non-callable value in application')
    if not isinstance(xs, LispList):
        raise LispError('second argument to apply not a list')
    return f(xs.val, env)

def lisp_progn(args, env):
    args = list(map(env.eval, args))
    if not args:
        raise LispError('no args given to progn')
    return args[-1]

def lisp_quote(args, env):
    if len(args) != 1:
        raise LispError('wrong number of args given to quote')
    return args[0]

def lisp_lambda(args, env):
    if len(args) != 2:
        raise LispError('wrong number of args given to quote')
    pars, body = args
    if not isinstance(pars, LispList):
        raise LispError('first argument to lambda not a list')
    if not all(isinstance(par, LispSymbol) for par in pars.val):
        raise LispError('first argument to lambda not a list of symbols')
    pars = [s.val for s in pars.val]
    clos = env.scopes.new_child()
    clos.maps.pop(0)
    return env.new(LispFunc(pars, body, 'anonymous function', clos))

def lisp_set(args, env):
    if len(args) != 2:
        raise LispError('wrong number of args given to set')
    name, val = args
    if not isinstance(name, LispSymbol):
        raise LispError('first argument to set not a symbol')
    val = env.eval(val)
    env[name.val] = val
    return val

def lisp_if(args, env):
    if len(args) != 3:
        raise LispError('wrong number of args given to if')
    cond, i, t, = args
    cond = env.eval(cond)
    if cond:
        return env.eval(i)
    else:
        return env.eval(t)

builtins = {
    'eval': lisp_eval,
    'apply': lisp_apply,
    'progn': lisp_progn,
    'quote': lisp_quote,
    'lambda': lisp_lambda,
    'set': lisp_set,
    'if': lisp_if
}

