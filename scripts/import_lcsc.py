# SPDX-FileCopyrightText: 2026 Emanuel Bachmann
# SPDX-License-Identifier: MIT
"""Copy parts fetched with easyeda2kicad into the project library.

    easyeda2kicad --full --lcsc_id=C123 --output <dir>/lib
    python3 -I import_lcsc.py <project_dir> <dir> [symbol names ...]

Symbols go into lib/SensorHAT.kicad_sym (footprint field pointed at SensorHAT:...),
footprints into lib/SensorHAT.pretty with the 3D model path made project-relative,
3D models into lib/SensorHAT.3dshapes. Existing entries with the same name are replaced.
"""
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sexpr import Q, dump, find, find_all, parse  # noqa: E402


def main(project_dir, src, *names):
    lib = os.path.join(project_dir, "lib")
    sym_path = os.path.join(lib, "SensorHAT.kicad_sym")
    tree = parse(open(sym_path, encoding="utf-8").read())
    new = parse(open(os.path.join(src, "lib.kicad_sym"), encoding="utf-8").read())
    wanted = set(names) or {str(s[1]) for s in find_all(new, "symbol")}
    footprints = set()
    for s in find_all(new, "symbol"):
        name = str(s[1])
        if name not in wanted:
            continue
        for pr in find_all(s, "property"):
            if str(pr[1]) == "Footprint":
                fp = str(pr[2]).split(":")[-1]
                pr[2] = Q("SensorHAT:" + fp)
                footprints.add(fp)
        tree[:] = [x for x in tree if not (isinstance(x, list) and x and x[0] == "symbol" and str(x[1]) == name)]
        tree.append(s)
        print("symbol", name)
    with open(sym_path, "w", encoding="utf-8") as f:
        f.write(dump(tree) + "\n")

    shapes = os.path.join(lib, "SensorHAT.3dshapes")
    os.makedirs(shapes, exist_ok=True)       # not in git: a fresh clone has no model folder
    for fp in sorted(footprints):
        t = parse(open(os.path.join(src, "lib.pretty", fp + ".kicad_mod"), encoding="utf-8").read())
        m = find(t, "model")
        if m:
            model = os.path.basename(str(m[1]))
            m[1] = Q("${KIPRJMOD}/lib/SensorHAT.3dshapes/" + model)
            for ext in (".wrl", ".step"):
                p = os.path.join(src, "lib.3dshapes", os.path.splitext(model)[0] + ext)
                if os.path.exists(p):
                    shutil.copy(p, shapes)
        with open(os.path.join(lib, "SensorHAT.pretty", fp + ".kicad_mod"), "w", encoding="utf-8") as f:
            f.write(dump(t) + "\n")
        print("footprint", fp)


if __name__ == "__main__":
    main(*sys.argv[1:])
