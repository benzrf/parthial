from collections import ChainMap
from camel import CamelRegistry
from .vals import LispSymbol, LispList, LispFunc, LispBuiltin
from .context import Context

def registry(globals):
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

    @parthial_types.dumper(Context, 'context', version=1)
    def _dump_context(ctx):
        return dict(scopes=ctx.scopes, max_things=ctx.max_things)

    @parthial_types.loader('context', version=1)
    def _load_context(d, ver):
        ctx = Context(globals, d['max_things'])
        ctx.scopes = d['scopes']
        for v in ctx.scopes.values():
            ctx.rec_new(v)
        return ctx

    return parthial_types

