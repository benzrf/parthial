from eval import *

def lispify(v):
    if isinstance(v, list):
        return LispList([lispify(v_) for v_ in v])
    elif isinstance(v, str):
        return LispSymbol(v)
    else:
        return v

def test(code, extra={}):
    ctx = builtins.copy()
    ctx.update(extra)
    i = EvalContext(ctx)
    res, t = i.run(lispify(code))
    print(res)
    print(list(t))

rec_limit_test = [['lambda', ['f'], ['f', 'f']], ['lambda', ['f'], ['f', 'f']]]

cl_test = [[['lambda', ['n'], ['lambda', [], 'n']], ['quote', 'x']]]

cl_test2 = [['lambda', ['n'], ['lambda', [], 'n']], ['quote', 'x']]

cl_eval_test = [[['lambda', [], ['progn', ['set', 'x', ['quote', 'z']], ['lambda', ['v'], ['eval', 'v']]]]], ['quote', 'x']]

