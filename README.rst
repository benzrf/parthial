NOT YET SUITABLE FOR PUBLIC USE
===============================

Parthial
========

Parthial is a simple Python implementation of a generic Lisp interpreter. It is
intended for use in user-scriptable server-side applications such as IRC bots.

Features
--------

Safe evaluation
~~~~~~~~~~~~~~~

Evaluation puts (configurably) strict limitations on recursion depth, number of
allocated values, and number of steps taken. The ``set`` built-in cannot mutate
parent scopes (so closures are immutable), and every other language feature
available in the package is purely functional.

Simple API
~~~~~~~~~~

Lisp values are represented by directly analogous Python objects; ``(a b c)``
is just ``LispList([LispSymbol('a'), LispSymbol('b'), LispSymbol('c')])``.
It's easy to define new built-ins, too:

::

    # part of the default_globals scope
    # suppresses evaluation of its arguments (quotes them)
    @built_in(default_globals, 'if', quotes=True)
    def lisp_if(self, env, cond, i, t):
        cond = env.eval(cond)
        if cond:
            return env.eval(i)
        else:
            return env.eval(t)

Serialization
~~~~~~~~~~~~~

PyYAML serializers and deserializers are provided for all Lisp value types, as
well as for definition contexts (built-ins are serialized by name, so a global
scope must be supplied at deserialization). Allocation limitations are kept
track of across serializtion, so it's safe and easy to give users a persistent
mutable environment.

Shortcomings
------------

No optimizations
~~~~~~~~~~~~~~~~

**Parthial is not a general-purpose interpreter.** There is no compilation or
optimization. It probably shouldn't be used to run any program that wouldn't be
appropriate, performance-wise, to implement as a shell script.

No code reviews (yet)
~~~~~~~~~~~~~~~~~~~~~

Nobody other than the original author has looked the code yet. For now, it'd be
unwise to actually expose an interpreter to the Internet at large, in case of
security holes.

No[t much] documentation (so far)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Working on it...

No tests (for now)
~~~~~~~~~~~~~~~~~~

The warning at the top is there for a reason.

