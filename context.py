from contextlib import contextmanager
from collections import ChainMap
from weakref import WeakSet
from .errs import LimitationError

class Context:
    def __init__(self, globals={}, max_things=5000):
        self.globals = globals
        self.scopes = ChainMap()
        self.max_things = max_things
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

    def new(self, val):
        if len(self.things) >= self.max_things:
            raise LimitationError('too many things')
        self.things.add(val)
        return val

    def rec_new(self, val):
        for child in val.children():
            self.rec_new(child)
        self.new(val)
        return val

    def add_rec_new(self, k, val):
        self.rec_new(val)
        self[k] = val
        return val

    def __getitem__(self, *args, **kwargs):
        chain = ChainMap(self.scopes, self.globals)
        return chain.__getitem__(*args, **kwargs)

    def __setitem__(self, *args, **kwargs):
        return self.scopes.__setitem__(*args, **kwargs)

    def __delitem__(self, *args, **kwargs):
        return self.scopes.__delitem__(*args, **kwargs)

    def __contains__(self, *args, **kwargs):
        chain = ChainMap(self.scopes, self.globals)
        return chain.__contains__(*args, **kwargs)

class EvalContext(Context):
    def __init__(self, globals={}, max_things=5000, max_depth=100, max_steps=10000):
        super().__init__(globals, max_things)
        self.max_depth, self.max_steps =\
                max_depth, max_steps
        self.depth = self.steps = 0

    def eval(self, expr):
        if self.depth >= self.max_depth:
            raise LimitationError('too much nesting')
        if self.steps >= self.max_steps:
            raise LimitationError('too many steps')
        self.depth += 1
        self.steps += 1
        res = expr.eval(self)
        self.depth -= 1
        return res

    def run(self, expr):
        self.rec_new(expr)
        res = self.eval(expr)
        return res, self.things

