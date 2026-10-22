# SPDX-FileCopyrightText: 2026 Emanuel Bachmann
# SPDX-License-Identifier: MIT
"""Bring the LCSC/EasyEDA sensor footprints in line with the manufacturers' land patterns.

Idempotent; run before gen_pcb.py (build.sh does). Usage: python3 -I patch_lib.py <project_dir>
- SCD41: centre pad 21 without paste plus four 1.8 x 1.8 mm paste windows at (+-1.25, +-1.25),
  perimeter paste 0.55 mm wide, solder mask 0.1 mm larger than the copper (Sensirion SCD4x
  datasheet v1.7, Fig. 4).
- VEML7700-TT: no legend circle under the package.
- Symbols: pin names hidden where EasyEDA draws them over the graphics (FETs, diodes, buzzer,
  switch); the small pin-1 dots removed, they sit on the pin names.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sexpr import Q, dump, find, find_all, parse, walk  # noqa: E402

LIB = "lib/SensorHAT.pretty"


def load(path):
    with open(path, encoding="utf-8") as f:
        return parse(f.read())


def save(path, tree):
    with open(path, "w", encoding="utf-8") as f:
        f.write(dump(tree) + "\n")


def set_child(node, key, *values):
    old = find(node, key)
    new = [key, *values]
    if old:
        node[node.index(old)] = new
    else:
        node.append(new)


def drop_silk_circles_inside(tree, x0, y0, x1, y1):
    keep = []
    for x in tree:
        if isinstance(x, list) and x and x[0] == "fp_circle" and find(x, "layer")[1] == "F.SilkS":
            c = find(x, "center")
            cx, cy = float(c[1]), float(c[2])
            if x0 < cx < x1 and y0 < cy < y1:
                continue
        keep.append(x)
    tree[:] = keep


def patch_scd41(tree):
    pads = find_all(tree, "pad")
    for p in pads:
        if p[1] == "21":
            set_child(p, "layers", "F.Cu", "F.Mask")
        elif p[1] != "":
            set_child(p, "solder_paste_margin", "-0.125")
        if p[1] != "":
            set_child(p, "solder_mask_margin", "0.1")
    if not any(p[1] == "" for p in pads):
        at = tree.index(pads[-1]) + 1
        for sx in (-1.25, 1.25):
            for sy in (-1.25, 1.25):
                tree.insert(at, ["pad", Q(""), "smd", "rect", ["at", sx, sy], ["size", 1.8, 1.8],
                                 ["layers", "F.Paste"]])


def patch_veml7700(tree):
    drop_silk_circles_inside(tree, -3.43, -2.54, 3.43, 0.38)


HIDE_PIN_NAMES = {"AO3400A", "1N4148W_C81598", "BAV70-C68978", "MLT-5020", "TS-1187A-B-A-B"}
PIN1_DOT_RADIUS = "0.38"


def drop_pin1_dots(node):
    for x in node:
        if isinstance(x, list):
            drop_pin1_dots(x)
    node[:] = [x for x in node if not (isinstance(x, list) and x and x[0] == "circle"
                                       and find(x, "radius") and str(find(x, "radius")[1]) == PIN1_DOT_RADIUS)]


def patch_symbols(path):
    """EasyEDA symbols come with 'unspecified' pin types, which ERC flags on every
    connection. Make them passive; VEML7700-TT keeps its explicit types."""
    tree = load(path)
    changed = 0
    for sym in find_all(tree, "symbol"):
        if sym[1] in HIDE_PIN_NAMES:
            new = ["pin_names", ["offset", "0.0254"], ["hide", "yes"]]
            old = find(sym, "pin_names")
            if old:
                sym[sym.index(old)] = new
            else:
                sym.insert(2, new)                # right after the symbol name, as KiCad writes it
        drop_pin1_dots(sym)
        if sym[1] == "VEML7700-TT":
            continue
        for p in walk(sym, "pin"):
            if len(p) > 1 and p[1] in ("unspecified", "input"):
                p[1] = "passive"
                changed += 1
    save(path, tree)
    return changed


def patch_sgp41(tree):
    """SGP41 exposed pad: copper 1.25 x 1.7, paste aperture 1.05 x 1.5 (datasheet Fig. 18)."""
    pads = find_all(tree, "pad")
    for p in pads:
        if p[1] == "7":
            set_child(p, "size", 1.25, 1.7)
            set_child(p, "layers", "F.Cu", "F.Mask")
    if not any(p[1] == "" for p in pads):
        tree.insert(tree.index(pads[-1]) + 1, ["pad", Q(""), "smd", "rect", ["at", 0, 0], ["size", 1.05, 1.5],
                                               ["layers", "F.Paste"]])


def fix_attr_and_holes(path):
    """easyeda2kicad quirks: unplated locating holes come as PTH pads with no copper, and the
    footprint type does not always match the pads."""
    tree = load(path)
    pads = find_all(tree, "pad")
    for p in pads:
        if p[2] == "thru_hole" and p[1] == "":
            size, drill = find(p, "size"), find(p, "drill")
            if size and drill and float(size[1]) <= float(drill[1]):
                p[2] = "np_thru_hole"
    # legend circles/texts that sit on a pad get clipped by the mask anyway: drop them
    def pad_boxes(x_is_text):
        boxes = []
        for p in pads:
            at, size = find(p, "at"), find(p, "size")
            if at and size:
                m = 0.8 if x_is_text else 0.15
                w, h = float(size[1]) / 2 + m, float(size[2]) / 2 + m
                if len(at) > 3 and abs(float(at[3])) % 180 == 90:
                    w, h = h, w
                boxes.append((float(at[1]) - w, float(at[2]) - h, float(at[1]) + w, float(at[2]) + h))

        return boxes

    circle_boxes, text_boxes = pad_boxes(False), pad_boxes(True)

    def on_pad(x, y, boxes):
        return any(x0 <= x <= x1 and y0 <= y <= y1 for x0, y0, x1, y1 in boxes)

    keep = []
    for x in tree:
        if isinstance(x, list) and x and x[0] in ("fp_circle", "fp_text") and find(x, "layer") \
                and find(x, "layer")[1] == "F.SilkS" and not (x[0] == "fp_text" and x[1] == "reference"):
            c = find(x, "center") if x[0] == "fp_circle" else find(x, "at")
            if c and on_pad(float(c[1]), float(c[2]), text_boxes if x[0] == "fp_text" else circle_boxes):
                continue
        keep.append(x)
    tree[:] = keep
    plated_tht = any(p[2] == "thru_hole" for p in pads)
    attr = find(tree, "attr")
    want = "through_hole" if plated_tht else "smd"
    if attr is None:
        tree.insert(2, ["attr", want])
    elif attr[1] != want:
        attr[1:] = [want]
    save(path, tree)


def main(project_dir):
    print("symbol pins set to passive:", patch_symbols(os.path.join(project_dir, "lib", "SensorHAT.kicad_sym")))
    lib_dir = os.path.join(project_dir, LIB)
    for f in sorted(os.listdir(lib_dir)):
        if f.endswith(".kicad_mod"):
            fix_attr_and_holes(os.path.join(lib_dir, f))
    lib = os.path.join(project_dir, LIB)
    for name, fn in (("LGA-20_L10.1-W10.1-P1.25-TL_SCD41-D-R2", patch_scd41),
                     ("SENSOR-SMD_EML7700-TT", patch_veml7700),
                     ("DFN-6_L2.4-W2.4-P0.80-TL-EP", patch_sgp41)):
        path = os.path.join(lib, name + ".kicad_mod")
        tree = load(path)
        fn(tree)
        save(path, tree)
        print("patched", name)


if __name__ == "__main__":
    main(sys.argv[1])
