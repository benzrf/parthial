from contextlib import contextmanager
from collections import ChainMap
from weakref import WeakSet

class InterpreterError(Exception):
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
        res = expr.eval(self)
        self.depth -= 1
        return res

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

    def __contains__(self, *args, **kwargs):
        return self.scopes.__contains__(*args, **kwargs)

