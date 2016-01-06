from .exprs import LispSymbol, LispList, LispFunc, LispError

def quotes(f):
    f.quote = True
    return f

def lisp_eval(args, env):
    if len(args) != 1:
        raise LispError('wrong number of args given to eval')
    return env.eval(args[0])

def lisp_apply(args, env):
    if len(args) != 2:
        raise LispError('wrong number of args given to apply')
    f, xs = args
    if not callable(f):
        raise LispError('non-callable value in application')
    if not isinstance(xs, LispList):
        raise LispError('second argument to apply not a list')
    return f(xs.val, env)

def lisp_progn(args, env):
    if not args:
        raise LispError('no args given to progn')
    return args[-1]

@quotes
def lisp_quote(args, env):
    if len(args) != 1:
        raise LispError('wrong number of args given to quote')
    return args[0]

@quotes
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

@quotes
def lisp_set(args, env):
    if len(args) != 2:
        raise LispError('wrong number of args given to set')
    name, val = args
    if not isinstance(name, LispSymbol):
        raise LispError('first argument to set not a symbol')
    val = env.eval(val)
    env[name.val] = val
    return val

@quotes
def lisp_if(args, env):
    if len(args) != 3:
        raise LispError('wrong number of args given to if')
    cond, i, t, = args
    cond = env.eval(cond)
    if cond:
        return env.eval(i)
    else:
        return env.eval(t)

built_ins = {
    'eval': lisp_eval,
    'apply': lisp_apply,
    'progn': lisp_progn,
    'quote': lisp_quote,
    'lambda': lisp_lambda,
    'set': lisp_set,
    'if': lisp_if
}

