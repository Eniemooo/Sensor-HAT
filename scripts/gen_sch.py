# SPDX-FileCopyrightText: 2026 Emanuel Bachmann
# SPDX-License-Identifier: MIT
"""Generate Sensor-HAT.kicad_sch from design.py.

Every connected pin gets a short wire stub and a net label; unconnected pins get
a no-connect flag. Usage: python3 -I gen_sch.py <project_dir>
"""
import os
import sys
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import design  # noqa: E402
import kicadlib  # noqa: E402
from sexpr import Q, dump  # noqa: E402

STUB = 2.54
FONT = [["font", ["size", 1.27, 1.27]]]


def uid(seed):
    return Q(str(uuid.uuid5(design.NAMESPACE, seed)))


def effects(hide=False, justify=None):
    e = ["effects"] + FONT
    if justify:
        e.append(["justify"] + justify)
    if hide:
        e.append(["hide", "yes"])
    return e


def prop(name, value, x, y, hide=False, angle=0):
    return ["property", Q(name), Q(value), ["at", x, y, angle], effects(hide)]


def snap(v):
    return round(v / 1.27) * 1.27


def main(project_dir):
    root_uuid = uid("root-sheet")
    lib_symbols = {}
    items = []
    labels = []
    wires = []
    no_connects = []
    texts = []

    for part in design.PARTS:
        lib_id = part["sym"]
        if lib_id not in lib_symbols:
            lib_symbols[lib_id] = kicadlib.load_symbol(lib_id)
        sym = lib_symbols[lib_id]
        sx, sy = snap(part["sch"][0]), snap(part["sch"][1])
        xmin, ymin, xmax, ymax = kicadlib.bbox(sym)
        pin_map = kicadlib.pins(sym)
        ref = part["ref"]
        is_power = ref.startswith("#")

        node = [
            "symbol",
            ["lib_id", Q(lib_id)],
            ["at", sx, sy, 0],
            ["unit", 1],
            ["exclude_from_sim", "no"],
            ["in_bom", "no" if is_power or part.get("no_bom") else "yes"],
            ["on_board", "no" if is_power else "yes"],
            ["dnp", "yes" if part.get("dnp") else "no"],
            ["uuid", uid("sym-" + ref)],
            prop("Reference", ref, sx, sy - ymax - 1.8, hide=is_power),
            prop("Value", part["value"], sx, sy - ymin + 1.8),
            prop("Footprint", part.get("fp", ""), sx, sy, hide=True),
            prop("Datasheet", part.get("datasheet", ""), sx, sy, hide=True),
            prop("Description", part.get("desc", ""), sx, sy, hide=True),
        ]
        for key in ("LCSC", "MPN", "Manufacturer"):
            if part.get(key):
                node.append(prop(key, part[key], sx, sy, hide=True))
        for num in pin_map:
            node.append(["pin", Q(num), ["uuid", uid(f"pin-{ref}-{num}")]])
        node.append(["instances", ["project", Q(design.PROJECT),
                                   ["path", Q("/" + root_uuid), ["reference", Q(ref)], ["unit", 1]]]])
        items.append(node)

        nets = part.get("pins", {})
        unknown = set(nets) - set(pin_map)
        if unknown:
            raise SystemExit(f"{ref}: pins {sorted(unknown)} not in symbol {lib_id} ({sorted(pin_map)})")
        for num, (px, py, ang, _name, ptype) in pin_map.items():
            x, y = sx + px, sy - py  # library Y is up, schematic Y is down
            net = nets.get(num)
            if net is None:
                if ptype != "no_connect" and not is_power:
                    no_connects.append(["no_connect", ["at", x, y], ["uuid", uid(f"nc-{ref}-{num}")]])
                continue
            if is_power:
                continue  # power flags connect through their own label below
            out = (ang + 180) % 360
            dx, dy = {0: (STUB, 0), 180: (-STUB, 0), 90: (0, -STUB), 270: (0, STUB)}[int(out)]
            ex, ey = x + dx, y + dy
            wires.append(["wire", ["pts", ["xy", x, y], ["xy", ex, ey]],
                          ["stroke", ["width", 0], ["type", "default"]], ["uuid", uid(f"w-{ref}-{num}")]])
            just = ["left", "bottom"] if out in (0, 90) else ["right", "bottom"]
            labels.append(["label", Q(net), ["at", ex, ey, out], effects(justify=just),
                           ["uuid", uid(f"lbl-{ref}-{num}")]])
        if is_power:
            # PWR_FLAG: pin 1 at the symbol origin, label sits right on it
            net = nets["1"]
            labels.append(["label", Q(net), ["at", sx, sy, 0], effects(justify=["left", "bottom"]),
                           ["uuid", uid(f"lbl-{ref}")]])

    for i, (txt, x, y, size) in enumerate(design.SCH_TEXTS):
        texts.append(["text", Q(txt), ["exclude_from_sim", "no"], ["at", x, y, 0],
                      ["effects", ["font", ["size", size, size], ["bold", "yes" if size > 1.5 else "no"]],
                       ["justify", "left", "bottom"]],
                      ["uuid", uid(f"text-{i}")]])

    sch = [
        "kicad_sch",
        ["version", "20250114"],
        ["generator", Q("eeschema")],
        ["generator_version", Q("9.0")],
        ["uuid", root_uuid],
        ["paper", Q("A2")],
        ["title_block", ["title", Q(design.TITLE)], ["date", Q(design.DATE)], ["rev", Q(design.REV)],
         ["company", Q(design.AUTHOR)]],
        ["lib_symbols"] + list(lib_symbols.values()),
    ]
    sch += texts + wires + labels + no_connects + items
    sch.append(["sheet_instances", ["path", Q("/"), ["page", Q("1")]]])
    sch.append(["embedded_fonts", "no"])

    out = os.path.join(project_dir, design.PROJECT + ".kicad_sch")
    with open(out, "w", encoding="utf-8") as f:
        f.write(dump(sch) + "\n")
    print("wrote", out, f"({len(items)} symbols, {len(labels)} labels, {len(no_connects)} no-connects)")


if __name__ == "__main__":
    main(sys.argv[1])
