from eval import *

def lispify(v):
    if isinstance(v, list):
        return LispList([lispify(v_) for v_ in v])
    elif isinstance(v, str):
        return LispSymbol(v)
    else:
        return v

def rec_limit_test():
    i = EvalContext({'lambda': lisp_lambda})
    nt = lispify([['lambda', ['f'], ['f', 'f']], ['lambda', ['f'], ['f', 'f']]])
    i.run(nt)

def cl_test():
    i = EvalContext({'lambda': lisp_lambda, 'x': 3})
    cl = [[['lambda', ['n'], ['lambda', [], 'n']], 'x']]
    res, t = i.run(lispify(cl))
    print(res)
    print(list(t))

def cl_test2():
    i = EvalContext({'lambda': lisp_lambda, 'x': 3})
    cl = [['lambda', ['n'], ['lambda', [], 'n']], 'x']
    res, t = i.run(lispify(cl))
    print(res)
    print(list(t))

