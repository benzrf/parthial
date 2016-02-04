"""
Classes for interpreter state.
"""

from contextlib import contextmanager
from collections import ChainMap
from weakref import WeakSet
from .errs import LimitationError

class Context:
    """A chain of scopes that tracks its own size.

    Args:
        globals (dict-like, optional): The global scope for this context.
        max_things (int, optional): The maximum number of values present in
            this context, after which no more may be added. Children of values
            bound to names are counted.
    """

    def __init__(self, globals={}, max_things=5000):
        self.globals = globals
        self.scopes = ChainMap()
        self.max_things = max_things
        self.things = WeakSet()

    @contextmanager
    def scopes_as(self, new_scopes):
        """Replace the scope chain used by this context for the duration of
            the with block.

        The global scope is not modified.

        Args:
            new_scopes (dict-like): The new scope chain to use.
        """
        old_scopes, self.scopes = self.scopes, new_scopes
        yield
        self.scopes = old_scopes

    @contextmanager
    def new_scope(self, new_scope={}):
        """Add a scope to the scope chain used by this context for the
            duration of the with block.

        Args:
            new_scope (dict-like): The scope to add.
        """
        old_scopes, self.scopes = self.scopes, self.scopes.new_child(new_scope)
        yield
        self.scopes = old_scopes

    def new(self, val):
        """Add a new value to this context.

        Args:
            val (LispVal): The value to be added.

        Returns:
            LispVal: The added value.

        Raises:
            LimitationError: If this context already contains the maximum
                number of values.
        """
        if len(self.things) >= self.max_things:
            raise LimitationError('too many things')
        self.things.add(val)
        return val

    def rec_new(self, val):
        """Recursively add a new value and its children to this context.

        Args:
            val (LispVal): The value to be added.

        Returns:
            LispVal: The added value.

        Raises:
            LimitationError: If this context already contains the maximum
                number of values.
        """
        for child in val.children():
            self.rec_new(child)
        self.new(val)
        return val

    def add_rec_new(self, k, val):
        """Recursively add a new value and its children to this context, and
            assign a variable to it.

        Args:
            k (str): The name of the variable to assign.
            val (LispVal): The value to be added and assigned.

        Returns:
            LispVal: The added value.

        Raises:
            LimitationError: If this context already contains the maximum
                number of values.
        """
        self.rec_new(val)
        self[k] = val
        return val

    def __getitem__(self, k):
        """Look up a variable.

        Args:
            k (str): The name of the variable to look up.

        Returns:
            LispVal: The value assigned to the variable.

        Raises:
            KeyError: If the variable has not been assigned to.
        """
        chain = ChainMap(self.scopes, self.globals)
        return chain.__getitem__(k)

    def __setitem__(self, k, val):
        """Assign to a variable.

        This will only mutate the innermost scope.

        Args:
            k (str): The name of the variable to assign to.
            val (LispVal): The value to assign to the variable.
        """
        self.scopes.__setitem__(k, val)

    def __delitem__(self, k):
        """Clear a variable.

        This will only mutate the innermost scope.

        Args:
            k (str): The name of the variable to clear.

        Raises:
            KeyError: If the variable has not been assigned to.
        """
        return self.scopes.__delitem__(k)

    def __contains__(self, k):
        """Check whether a variable has been assigned to.

        Args:
            k (str): The name of the variable to check.

        Returns:
            bool: Whether or not the variable has been assigned to.
        """
        chain = ChainMap(self.scopes, self.globals)
        return chain.__contains__(k)

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

