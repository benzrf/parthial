from collections import ChainMap
from camel import CamelRegistry
from .vals import LispSymbol, LispList, LispFunc, LispBuiltin
from .context import Environment

def registry(globals):
    """Get a :class:`camel.CamelRegistry` for [de]serializing your Parthial
    objects.

    The registry will support [de]serializing instances of all standard
    :class:`~parthial.vals.LispVal` subclasses, as well as
    :class:`Environments <parthial.context.Environment>`.

    Args:
        globals (dict-like): The set of globals to initialize deserialized
            :class:`Environments <parthial.context.Environment>` with.

    Returns:
        camel.CamelRegistry: The registry.
    """

    parthial_types = CamelRegistry()

    @parthial_types.dumper(ChainMap, 'chainmap', version=1)
    def _dump_chainmap_v1(cm):
        return cm.maps

    @parthial_types.loader('chainmap', version=1)
    def _load_chainmap_v1(ms, ver):
        return ChainMap(*ms)

    @parthial_types.dumper(LispSymbol, 'lispsym', version=1)
    def _dump_symbol_v1(sym):
        return sym.val

    @parthial_types.loader('lispsym', version=1)
    def _load_symbol_v1(s, ver):
        return LispSymbol(s)

    @parthial_types.dumper(LispList, 'lisplist', version=1)
    def _dump_list_v1(list):
        return list.val

    @parthial_types.loader('lisplist', version=1)
    def _load_list_v1(l, ver):
        return LispList(l)

    @parthial_types.dumper(LispFunc, 'lispfunc', version=1)
    def _dump_func_v1(func):
        return dict(
            pars=func.pars,
            body=func.body,
            name=func.name,
            clos=func.clos
        )

    @parthial_types.loader('lispfunc', version=1)
    def _load_func_v1(d, ver):
        return LispFunc(d['pars'], d['body'], d['name'], d['clos'])

    @parthial_types.dumper(LispBuiltin, 'lispbuiltin', version=1)
    def _dump_bi_v1(bi):
        return bi.name

    @parthial_types.loader('lispbuiltin', version=1)
    def _load_bi_v1(n, ver):
        return globals[n]

    @parthial_types.dumper(Environment, 'environment', version=1)
    def _dump_context(env):
        return dict(scopes=env.scopes, max_things=env.max_things)

    @parthial_types.loader('environment', version=1)
    def _load_context(d, ver):
        env = Environment(globals, d['max_things'])
        env.scopes = d['scopes']
        for v in env.scopes.values():
            env.rec_new(v)
        return env

    return parthial_types

