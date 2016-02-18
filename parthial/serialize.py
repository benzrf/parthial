from collections import ChainMap
from weakref import WeakSet
from functools import partial
import yaml
from .vals import LispSymbol, LispList, LispFunc, LispBuiltin
from .context import Environment

class ParthialDumper(yaml.SafeDumper):
    """Dumper class for :class:`~parthial.vals.LispVal` subclasses and
    :class:`Environments <parthial.context.Environment>`.
    """
dumper = lambda c: partial(ParthialDumper.add_representer, c)

class ParthialLoader(yaml.SafeLoader):
    """Loader class for :class:`~parthial.vals.LispVal` subclasses and
    :class:`Environments <parthial.context.Environment>`.

    Args:
        globals (dict-like): The set of globals to look up builtins in and
        initialize deserialized
        :class:`Environments <parthial.context.Environment>` with.
    """
    def __init__(self, globals, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.globals = globals
loader = lambda t: partial(ParthialLoader.add_constructor, t)

@dumper(WeakSet)
def weakset_representer(dumper, data):
    value = {}
    for key in data:
        value[key] = None
    return dumper.represent_mapping('!weakset;1', value)

@loader('!weakset;1')
def weakset_constructor(loader, node):
    data = WeakSet()
    yield data
    value = loader.construct_mapping(node)
    data.update(value)

@dumper(ChainMap)
def chainmap_representer(dumper, data):
    return dumper.represent_sequence('!chainmap;1', data.maps)

@loader('!chainmap;1')
def chainmap_constructor(loader, node):
    data = ChainMap()
    yield data
    value = loader.construct_sequence(node)
    data.maps = value

@dumper(LispSymbol)
def lispsymbol_representer(dumper, data):
    return dumper.represent_scalar('!lispsymbol;1', data.val)

@loader('!lispsymbol;1')
def lispsymbol_constructor(loader, node):
    return LispSymbol(loader.construct_scalar(node))

@dumper(LispList)
def lisplist_representer(dumper, data):
    return dumper.represent_sequence('!lisplist;1', data.val)

@loader('!lisplist;1')
def lisplist_constructor(loader, node):
    data = LispList(None)
    yield data
    data.val = loader.construct_sequence(node)

@dumper(LispFunc)
def lispfunc_representer(dumper, data):
    rep = dict(
        pars=data.pars,
        body=data.body,
        name=data.name,
        clos=data.clos,
    )
    return dumper.represent_mapping('!lispfunc;1', rep)

@loader('!lispfunc;1')
def lispfunc_constructor(loader, node):
    data = LispFunc(None, None, None, None)
    yield data
    rep = loader.construct_mapping(node)
    data.pars, data.body, data.name, data.clos =\
        rep['pars'], rep['body'], rep['name'], rep['clos']

@dumper(LispBuiltin)
def lispbuiltin_representer(dumper, data):
    return dumper.represent_scalar('!lispbuiltin;1', data.name)

@loader('!lispbuiltin;1')
def lispbuiltin_constructor(loader, node):
    return loader.globals[loader.construct_scalar(node)]

@dumper(Environment)
def environment_representer(dumper, data):
    rep = dict(
        scopes=data.scopes,
        max_things=data.max_things,
        things=data.things,
    )
    return dumper.represent_mapping('!environment;1', rep)

@loader('!environment;1')
def environment_constructor(loader, node):
    data = Environment(loader.globals, None)
    yield data
    rep = loader.construct_mapping(node)
    data.scopes, data.max_things, data.things =\
        rep['scopes'], rep['max_things'], rep['things']

