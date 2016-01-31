NOT YET SUITABLE FOR PUBLIC USE
===============================

Parthial
========

Parthial is a simple Python implementation of a generic Lisp
interpreter. It is intended for use in user-scriptable server-side
applications such as IRC bots.

Features
--------

Safe evaluation
~~~~~~~~~~~~~~~

Evaluation puts (configurably) strict limitations on recursion depth,
number of allocated values, and number of steps taken. The ``set``
built-in cannot mutate parent scopes (so closures are immutable), and
everything else available in the package is purely functional.

Simple API
~~~~~~~~~~

Lisp values are represented by directly analogous Python objects;
``(a b c)`` is just
``LispList([LispSymbol('a'), LispSymbol('b'), LispSymbol('c')])``.
Defining new built-ins is as straightforward as

::

    @built_in(default_globals, 'if', quotes=True)
    def lisp_if(self, env, cond, i, t):
        cond = env.eval(cond)
        if cond:
            return env.eval(i)
        else:
            return env.eval(t)

Serialization
~~~~~~~~~~~~~

Camel_ serializers and deserializers are provided for all Lisp value types,
as well as for definition contexts.

.. _Camel: https://pypi.python.org/pypi/camel/0.1

Shortcomings
------------

No optimizations
~~~~~~~~~~~~~~~~

**Parthial is not a general-purpose interpreter.** There is no
compilation or optimization. You probably shouldn't use it to run any
program that wouldn't be appropriate to implement as a shell script.

No code reviews (yet)
~~~~~~~~~~~~~~~~~~~~~

Nobody other than me (benzrf) has looked the code yet. For now, it'd be
unwise to actually expose an interpreter to the Internet at large, in
case of security holes.

No documentation (so far)
~~~~~~~~~~~~~~~~~~~~~~~~~

I'll probably get around to it eventually...

No tests (for now)
~~~~~~~~~~~~~~~~~~

The warning at the top is there for a reason.

