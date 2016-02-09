"""
Classes for interpreter state.
"""

from contextlib import contextmanager
from collections import ChainMap
from weakref import WeakSet
from .errs import LimitationError

class Context:
    """A chain of scopes that tracks its elements.

    A :class:`LispVal` "is an element of" a :class:`Context` when it is
    indirectly referenced by it (i.e., when the :class:`LispVal` cannot be
    garbage collected until the :class:`Context` is). In order for
    :class:`Contexts <Context>` to keep track of their elements, they must be
    manually notified of any new values that may enter them. Therefore, **any**
    code that allocates a :class:`LispVal` **must** immediately
    :meth:`add <new>` it to any :class:`Contexts <Context>` that it may become
    an element of.

    Attributes:
        scopes (list of dict-likes): My chain of scopes. Earlier scopes are
            deeper.

    Args:
        globals (dict-like, optional): My global scope.
        max_things (int, optional): The maximum number of elements that I may
            contain, after which no more may be added.
    """

    def __init__(self, globals={}, max_things=5000):
        self.globals = globals
        self.scopes = ChainMap()
        self.max_things = max_things
        self.things = WeakSet()

    @contextmanager
    def scopes_as(self, new_scopes):
        """Replace my :attr:`scopes` for the duration of the with block.

        My global scope is not replaced.

        Args:
            new_scopes (list of dict-likes): The new :attr:`scopes` to use.
        """
        old_scopes, self.scopes = self.scopes, new_scopes
        yield
        self.scopes = old_scopes

    @contextmanager
    def new_scope(self, new_scope={}):
        """Add a new innermost scope for the duration of the with block.

        Args:
            new_scope (dict-like): The scope to add.
        """
        old_scopes, self.scopes = self.scopes, self.scopes.new_child(new_scope)
        yield
        self.scopes = old_scopes

    def new(self, val):
        """Add a new value to me.

        Args:
            val (LispVal): The value to be added.

        Returns:
            LispVal: The added value.

        Raises:
            LimitationError: If I already contain the maximum number of
                elements.
        """
        if len(self.things) >= self.max_things:
            raise LimitationError('too many things')
        self.things.add(val)
        return val

    def rec_new(self, val):
        """Recursively add a new value and its children to me.

        Args:
            val (LispVal): The value to be added.

        Returns:
            LispVal: The added value.
        """
        for child in val.children():
            self.rec_new(child)
        self.new(val)
        return val

    def add_rec_new(self, k, val):
        """Recursively add a new value and its children to me, and assign a
        variable to it.

        Args:
            k (str): The name of the variable to assign.
            val (LispVal): The value to be added and assigned.

        Returns:
            LispVal: The added value.
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

        This will only mutate my innermost scope.

        This does **not** :meth:`add <new>` anything to me.

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
    """A :class:`Context` that tracks the progress of the evaluation of an
    expression.

    Attributes:
        depth (int): The current level of nesting. This measures nested calls to
            :meth:`eval`, not actual Python stack frames, so you'll get an
            overflow when it reaches about a third of your stack size. In order
            for this to be a good enough measure of depth to keep evaluation
            safe, extensions must always accomplish potentially-unbounded
            recursion through :meth:`eval`.
        steps (int): The number of steps that have been taken. One "step" is one
            call to :meth:`eval`, so :attr:`steps` is only roughly proportional
            to actual time taken. In order for this to be a good enough
            metric to keep evaluation safe, extensions must always accomplish
            potentially-unbounded computation through :meth:`eval`.
            Additionally, they must always carefully limit the potential size
            of result values, since arbitrarily large ones could result in
            arbitrarily long computations with only one :meth:`eval`
            invocation (e.g., in a Bignum extension).

    Args:
        max_depth (int, optional): The maximum value that :attr:`depth` may
            reach, after which :meth:`eval` may not be called. You should not
            set this to more than about a quarter of your stack depth at most.
        max_steps (int, optional): The maximum number of steps that may be
            taken during evaluation.
    """
    def __init__(self, globals={}, max_things=5000, max_depth=100,\
            max_steps=10000):
        super().__init__(globals, max_things)
        self.max_depth, self.max_steps =\
                max_depth, max_steps
        self.depth = self.steps = 0

    def eval(self, expr):
        """Evaluate an expression.

        This does **not** add its argument (or its result) as an element of me!
        That is the responsibility of the code that created the object. This
        means that you need to :meth:`Context.rec_new` any expression you get
        from user input before evaluating it.

        This, and any wrappers around it, are the **only** entry points to
        expression evaluation you should call from ordinary code (i.e., code
        that isn't part of a extension).

        Args:
            expr (LispVal): The expression to evaluate.

        Returns:
            LispVal: The result of evaluating the expression.

        Raises:
            LimitationError: If evaluating the expression would require more
                nesting, more time, or the allocation of more values than is
                permissible.
        """
        if self.depth >= self.max_depth:
            raise LimitationError('too much nesting')
        if self.steps >= self.max_steps:
            raise LimitationError('too many steps')
        self.depth += 1
        self.steps += 1
        res = expr.eval(self)
        self.depth -= 1
        return res

    @classmethod
    def eval_in_new(cls, expr, *args, **kwargs):
        """:meth:`eval` an expression in a new, temporary :class:`EvalContext`.

        This should be safe to use directly on user input.

        Args:
            expr (LispVal): The expression to evaluate.
            *args: Args for the :class:`EvalContext` constructor.
            **kwargs: Kwargs for the :class:`EvalContext` constructor.
        """
        ctx = cls(*args, **kwargs)
        ctx.rec_new(expr)
        return ctx.eval(expr)

