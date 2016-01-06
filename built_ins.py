from functools import partial
from .exprs import LispSymbol, LispList, LispFunc, LispError

class LispBuiltin:
    built_ins = {}

    def __init__(self, name, f, quotes=False):
        self.f, self.name, self.quotes = f, name, quotes
        LispBuiltin.built_ins[name] = f

    def __call__(self, *args, **kwargs):
        return self.f(*args, **kwargs)

    def __str__(self):
        return self.name

built_ins = LispBuiltin.built_ins

def builtin(*args, **kwargs):
    return partial(LispBuiltin, *args, **kwargs)

@builtin('eval')
def lisp_eval(args, env):
    if len(args) != 1:
        raise LispError('wrong number of args given to eval')
    return env.eval(args[0])

@builtin('apply')
def lisp_apply(args, env):
    if len(args) != 2:
        raise LispError('wrong number of args given to apply')
    f, xs = args
    if not callable(f):
        raise LispError('non-callable value in application')
    if not isinstance(xs, LispList):
        raise LispError('second argument to apply not a list')
    return f(xs.val, env)

@builtin('progn')
def lisp_progn(args, env):
    if not args:
        raise LispError('no args given to progn')
    return args[-1]

@builtin('quote', quotes=True)
def lisp_quote(args, env):
    if len(args) != 1:
        raise LispError('wrong number of args given to quote')
    return args[0]

@builtin('lambda', quotes=True)
def lisp_lambda(args, env):
    if len(args) != 2:
        raise LispError('wrong number of args given to lambda')
    pars, body = args
    if not isinstance(pars, LispList):
        raise LispError('first argument to lambda not a list')
    if not all(isinstance(par, LispSymbol) for par in pars.val):
        raise LispError('first argument to lambda not a list of symbols')
    pars = [s.val for s in pars.val]
    clos = env.scopes.new_child()
    clos.maps.pop(0)
    return env.new(LispFunc(pars, body, 'anonymous function', clos))

@builtin('set', quotes=True)
def lisp_set(args, env):
    if len(args) != 2:
        raise LispError('wrong number of args given to set')
    name, val = args
    if not isinstance(name, LispSymbol):
        raise LispError('first argument to set not a symbol')
    val = env.eval(val)
    env[name.val] = val
    return val

@builtin('if', quotes=True)
def lisp_if(args, env):
    if len(args) != 3:
        raise LispError('wrong number of args given to if')
    cond, i, t, = args
    cond = env.eval(cond)
    if cond:
        return env.eval(i)
    else:
        return env.eval(t)

