from functools import partial, wraps
from .vals import LispSymbol, LispList, LispFunc, LispBuiltin
from .errs import LispError, LimitationError, LispArgTypeError, UncallableError, ArgCountError

default_globals = {}

def built_in(d, *args, count_args=True, **kwargs):
    def _(f):
        if count_args:
            arg_count = f.__code__.co_argcount - 2
            @wraps(f)
            def wrapped(self, ctx, args):
                if len(args) == arg_count:
                    return f(self, ctx, *args)
                else:
                    raise ArgCountError(self, len(args), arg_count)
        else:
            wrapped = f
        b = LispBuiltin(wrapped, *args, **kwargs)
        d[b.name] = b
        return b
    return _

def check_type(self, v, t, arg):
    if not isinstance(v, t):
        raise LispArgTypeError(self, v, t, arg)

@built_in(default_globals, 'eval')
def lisp_eval(self, ctx, code):
    return ctx.eval(code)

@built_in(default_globals, 'apply')
def lisp_apply(self, ctx, f, xs):
    if not callable(f):
        raise UncallableError(f)
    check_type(self, xs, LispList, 2)
    return f(xs.val, ctx)

@built_in(default_globals, 'progn', count_args=False)
def lisp_progn(self, ctx, args):
    if not args:
        raise ArgCountError(self, 0, '>= 1')
    return args[-1]

@built_in(default_globals, 'quote', quotes=True)
def lisp_quote(self, ctx, val):
    return val

@built_in(default_globals, 'lambda', quotes=True)
def lisp_lambda(self, ctx, pars, body):
    check_type(self, pars, LispList, 1)
    if not all(isinstance(par, LispSymbol) for par in pars.val):
        raise LispArgTypeError(self, pars, 'list of symbols', 1)
    pars = [s.val for s in pars.val]
    clos = ctx.env.scopes.new_child()
    clos.maps.pop(0)
    return ctx.env.new(LispFunc(pars, body, 'anonymous function', clos))

@built_in(default_globals, 'set', quotes=True)
def lisp_set(self, ctx, name, val):
    check_type(self, name, LispSymbol, 1)
    val = ctx.eval(val)
    ctx.env[name.val] = val
    return val

@built_in(default_globals, 'if', quotes=True)
def lisp_if(self, ctx, cond, i, t):
    cond = ctx.eval(cond)
    if cond:
        return ctx.eval(i)
    else:
        return ctx.eval(t)

@built_in(default_globals, 'cons')
def lisp_cons(self, ctx, h, t):
    check_type(self, t, LispList, 2)
    if len(t.val) > 1023:
        raise LimitationError('cons would create too long a list')
    return ctx.env.new(LispList([h] + t.val))

@built_in(default_globals, 'car')
def lisp_car(self, ctx, l):
    check_type(self, l, LispList, 1)
    if not l.val:
        raise LispError('car of empty list')
    return l.val[0]

@built_in(default_globals, 'cdr')
def lisp_cdr(self, ctx, l):
    check_type(self, l, LispList, 1)
    cdr = l.val[1:]
    return ctx.env.new(LispList(cdr))

@built_in(default_globals, 'list', count_args=False)
def lisp_list(self, ctx, l):
    if len(l) > 1024:
        raise LispError('too many items in list')
    return ctx.env.new(LispList(l))

