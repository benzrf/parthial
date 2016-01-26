from functools import partial
from .vals import LispError, LispSymbol, LispList, LispFunc, LispBuiltin

built_ins = {}

def built_in(d, *args, **kwargs):
    def _(f):
        b = LispBuiltin(f, *args, **kwargs)
        d[b.name] = b
        return b
    return _

@built_in(built_ins, 'eval')
def lisp_eval(args, env):
    if len(args) != 1:
        raise LispError('wrong number of args given to eval')
    return env.eval(args[0])

@built_in(built_ins, 'apply')
def lisp_apply(args, env):
    if len(args) != 2:
        raise LispError('wrong number of args given to apply')
    f, xs = args
    if not callable(f):
        raise LispError('non-callable value in application')
    if not isinstance(xs, LispList):
        raise LispError('second argument to apply not a list')
    return f(xs.val, env)

@built_in(built_ins, 'progn')
def lisp_progn(args, env):
    if not args:
        raise LispError('no args given to progn')
    return args[-1]

@built_in(built_ins, 'quote', quotes=True)
def lisp_quote(args, env):
    if len(args) != 1:
        raise LispError('wrong number of args given to quote')
    return args[0]

@built_in(built_ins, 'lambda', quotes=True)
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

@built_in(built_ins, 'set', quotes=True)
def lisp_set(args, env):
    if len(args) != 2:
        raise LispError('wrong number of args given to set')
    name, val = args
    if not isinstance(name, LispSymbol):
        raise LispError('first argument to set not a symbol')
    val = env.eval(val)
    env[name.val] = val
    return val

@built_in(built_ins, 'if', quotes=True)
def lisp_if(args, env):
    if len(args) != 3:
        raise LispError('wrong number of args given to if')
    cond, i, t, = args
    cond = env.eval(cond)
    if cond:
        return env.eval(i)
    else:
        return env.eval(t)

@built_in(built_ins, 'cons')
def lisp_cons(args, env):
    if len(args) != 2:
        raise LispError('wrong number of args given to cons')
    h, t = args
    if not isinstance(t, LispList):
        raise LispError('second argument to cons not a list')
    return env.new(LispList([h] + t.val))

