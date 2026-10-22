# SPDX-FileCopyrightText: 2026 Emanuel Bachmann
# SPDX-License-Identifier: MIT
"""Load symbols from KiCad .kicad_sym libraries (flattening `extends`)."""
import copy
import os

from sexpr import Q, parse, find, find_all, walk

KICAD_SHARE = os.path.expanduser("~/Applications/KiCad/KiCad.app/Contents/SharedSupport")
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LIB_PATHS = {
    "SensorHAT": os.path.join(PROJECT_DIR, "lib", "SensorHAT.kicad_sym"),
}

_cache = {}


def _lib(name):
    if name not in _cache:
        path = LIB_PATHS.get(name) or os.path.join(KICAD_SHARE, "symbols", name + ".kicad_sym")
        with open(path, encoding="utf-8") as f:
            tree = parse(f.read())
        _cache[name] = {s[1]: s for s in find_all(tree, "symbol")}
    return _cache[name]


def _rename_units(node, old, new):
    for sub in find_all(node, "symbol"):
        if sub[1].startswith(old + "_"):
            sub[1] = Q(new + sub[1][len(old):])


def load_symbol(lib_id):
    """Return a flattened symbol node named 'Lib:Name' ready for lib_symbols."""
    lib, name = lib_id.split(":", 1)
    syms = _lib(lib)
    sym = copy.deepcopy(syms[name])
    ext = find(sym, "extends")
    if ext:
        parent = load_symbol(lib + ":" + ext[1])
        parent_name = parent[1].split(":", 1)[1]
        flat = copy.deepcopy(parent)
        child_props = {p[1]: p for p in find_all(sym, "property")}
        for i, x in enumerate(flat):
            if isinstance(x, list) and x and x[0] == "property" and x[1] in child_props:
                flat[i] = child_props.pop(x[1])
        # remaining child-only properties go right after the parent's properties
        last_prop = max(i for i, x in enumerate(flat) if isinstance(x, list) and x and x[0] == "property")
        for p in child_props.values():
            last_prop += 1
            flat.insert(last_prop, p)
        _rename_units(flat, parent_name, name)
        sym = flat
    sym[1] = Q(lib_id)
    return sym


def pins(sym):
    """{number: (x, y, angle, name, type)} in library coordinates (Y up)."""
    out = {}
    for p in walk(sym, "pin"):
        if len(p) < 3 or isinstance(p[1], list):
            continue
        at = find(p, "at")
        num = find(p, "number")
        nm = find(p, "name")
        if at is None or num is None:
            continue
        ang = float(at[3]) if len(at) > 3 else 0.0
        out[str(num[1])] = (float(at[1]), float(at[2]), ang, str(nm[1]) if nm else "", str(p[1]))
    return out


def bbox(sym):
    """Rough (xmin, ymin, xmax, ymax) in library coordinates."""
    xs, ys = [], []
    for x, y, _a, _n, _t in pins(sym).values():
        xs.append(x)
        ys.append(y)
    for r in walk(sym, "rectangle"):
        for k in ("start", "end"):
            pt = find(r, k)
            xs.append(float(pt[1]))
            ys.append(float(pt[2]))
    for pl in walk(sym, "xy"):
        xs.append(float(pl[1]))
        ys.append(float(pl[2]))
    for c in walk(sym, "circle"):
        ctr = find(c, "center")
        rad = find(c, "radius")
        if ctr and rad:
            xs += [float(ctr[1]) - float(rad[1]), float(ctr[1]) + float(rad[1])]
            ys += [float(ctr[2]) - float(rad[1]), float(ctr[2]) + float(rad[1])]
    if not xs:
        return (-2.54, -2.54, 2.54, 2.54)
    return (min(xs), min(ys), max(xs), max(ys))
