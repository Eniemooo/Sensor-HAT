# SPDX-FileCopyrightText: 2026 Emanuel Bachmann
# SPDX-License-Identifier: MIT
"""Export JLCPCB production files, PDFs and renders.

Usage: python3 -I export.py <project_dir>
Writes <project_dir>/production/ (gerber zip, BOM, CPL) and <project_dir>/docs/.
"""
import csv
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile
from collections import OrderedDict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import design  # noqa: E402

CLI = os.path.expanduser("~/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli")
LAYERS = "F.Cu,In1.Cu,In2.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts"


def run(*args):
    r = subprocess.run([CLI, *args], capture_output=True, text=True)
    out = "\n".join(line for line in (r.stdout + r.stderr).splitlines() if "Fontconfig" not in line)
    if r.returncode != 0:
        raise SystemExit(f"kicad-cli {' '.join(args[:3])} failed:\n{out}")
    return out


KPY = os.path.expanduser("~/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3")
PAD_CENTRES = """
import json, sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1])
o = b.GetDesignSettings().GetAuxOrigin()
out = {}
for fp in b.GetFootprints():
    if fp.GetReference() in sys.argv[2:]:
        xs = [q.GetPosition().x for q in fp.Pads()]
        ys = [q.GetPosition().y for q in fp.Pads()]
        cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
        out[fp.GetReference()] = [round(pcbnew.ToMM(int(cx - o.x)), 4), round(-pcbnew.ToMM(int(cy - o.y)), 4)]
print(json.dumps(out))
"""


def pad_centres(pcb, refs):
    """Pad bounding-box centres (aux origin, Y up): JLC wants the body centre for connectors."""
    r = subprocess.run([KPY, "-I", "-c", PAD_CENTRES, pcb, *refs], capture_output=True, text=True)
    lines = [line for line in r.stdout.splitlines() if line.startswith("{")]
    if not lines:
        raise SystemExit("pad centre helper failed:\n" + r.stderr[-2000:])
    return json.loads(lines[-1])


def sort_key(ref):
    return ref[0], int("".join(c for c in ref if c.isdigit()) or 0)


def write_jlc(prod, variant, with_hand, pos, centres):
    parts = [p for p in design.PARTS
             if not p["ref"].startswith("#") and not p.get("no_bom") and p.get("LCSC")
             and (with_hand or not p.get("hand")) and not p.get("hand_only")]
    rows = []
    for p in parts:
        r = pos.get(p["ref"])
        if r is None:
            continue
        x, y = float(r["PosX"]), float(r["PosY"])
        if p["ref"] in centres:
            x, y = centres[p["ref"]]
        rot = (float(r["Rot"]) + p.get("jlc_rot", 0)) % 360
        rows.append([p["ref"], f"{x:.4f}mm", f"{y:.4f}mm",
                     "Top" if r["Side"].lower().startswith("top") else "Bottom", f"{rot:g}"])
    with open(os.path.join(prod, f"{design.PROJECT}-CPL-{variant}.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Designator", "Mid X", "Mid Y", "Layer", "Rotation"])
        w.writerows(sorted(rows, key=lambda x: sort_key(x[0])))

    groups = OrderedDict()
    for p in parts:
        g = groups.setdefault(p["LCSC"], {"value": p["value"], "fp": p["fp"].split(":", 1)[1], "refs": [],
                                          "mpn": p.get("MPN", ""), "mfr": p.get("Manufacturer", "")})
        g["refs"].append(p["ref"])
    with open(os.path.join(prod, f"{design.PROJECT}-BOM-{variant}.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #", "Quantity", "Manufacturer", "MPN"])
        for lcsc, g in groups.items():
            w.writerow([g["value"], ",".join(sorted(g["refs"], key=sort_key)), g["fp"], lcsc, len(g["refs"]),
                        g["mfr"], g["mpn"]])


def main(project_dir):
    pcb = os.path.join(project_dir, design.PROJECT + ".kicad_pcb")
    sch = os.path.join(project_dir, design.PROJECT + ".kicad_sch")
    prod = os.path.join(project_dir, "production")
    docs = os.path.join(project_dir, "docs")
    gdir = os.path.join(project_dir, "build", "gerber")
    for d in (prod, docs):
        os.makedirs(d, exist_ok=True)
    shutil.rmtree(gdir, ignore_errors=True)
    os.makedirs(gdir)

    # Gerbers + drill (JLCPCB: Protel extensions, drill/place origin, Excellon mm decimal)
    run("pcb", "export", "gerbers", "--layers", LAYERS, "--subtract-soldermask", "--use-drill-file-origin",
        "--no-x2", "-o", gdir + "/", pcb)
    run("pcb", "export", "drill", "--format", "excellon", "--excellon-units", "mm",
        "--excellon-zeros-format", "decimal", "--excellon-oval-format", "alternate",
        "--drill-origin", "plot", "--generate-map", "--map-format", "gerberx2", "-o", gdir + "/", pcb)
    zpath = os.path.join(prod, f"{design.PROJECT}-gerber-jlcpcb.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(os.listdir(gdir)):
            z.write(os.path.join(gdir, f), f)

    # Positions -> JLCPCB CPL. Two variants:
    #   "jlcpcb"          SMD only (headers J1-J3 soldered by hand)
    #   "jlcpcb-komplett" everything incl. the through-hole headers (JLC THT assembly)
    pos_csv = os.path.join(project_dir, "build", "pos.csv")
    run("pcb", "export", "pos", "--format", "csv", "--units", "mm", "--side", "both",
        "--use-drill-file-origin", "--exclude-dnp", "-o", pos_csv, pcb)
    with open(pos_csv, newline="", encoding="utf-8") as f:
        pos = {r["Ref"]: r for r in csv.DictReader(f)}
    centres = pad_centres(pcb, [p["ref"] for p in design.PARTS if p.get("hand")])
    for variant, with_hand in (("jlcpcb", False), ("jlcpcb-komplett", True)):
        write_jlc(prod, variant, with_hand, pos, centres)

    # hand-soldered parts (headers; J1 goes on the bottom side)
    with open(os.path.join(prod, f"{design.PROJECT}-BOM-handloeten.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Designator", "Comment", "LCSC Part #", "MPN", "Manufacturer", "Note"])
        for p in design.PARTS:
            if p.get("hand"):
                w.writerow([p["ref"], p["value"], p["LCSC"], p["MPN"], p["Manufacturer"], p.get("desc", "")])

    # Documentation
    run("sch", "export", "pdf", "-o", os.path.join(docs, f"{design.PROJECT}-Schaltplan.pdf"), sch)
    run("pcb", "export", "pdf", "--layers", "F.Fab,Edge.Cuts,F.Silkscreen", "--mode-single",
        "--include-border-title", "-o", os.path.join(docs, f"{design.PROJECT}-Bestueckung-oben.pdf"), pcb)
    run("pcb", "export", "pdf", "--layers", "B.Fab,Edge.Cuts,B.Silkscreen", "--mode-single", "--mirror",
        "--include-border-title", "-o", os.path.join(docs, f"{design.PROJECT}-Bestueckung-unten.pdf"), pcb)

    # Renders and STEP need the LCSC 3D models, which are not in git (scripts/fetch_3d_models.py)
    shapes = os.path.join(project_dir, "lib", "SensorHAT.3dshapes")
    with open(pcb, encoding="utf-8") as f:
        models = set(re.findall(r'"\$\{KIPRJMOD\}/lib/SensorHAT\.3dshapes/([^"]+)"', f.read()))
    missing = sorted(m for m in models if not os.path.exists(os.path.join(shapes, m)))
    if missing:
        print(f"{len(missing)} 3D models missing (run scripts/fetch_3d_models.py first): renders and STEP skipped")
        print("exported:", sorted(os.listdir(prod)), sorted(os.listdir(docs)))
        return
    for side in ("top", "bottom"):
        run("pcb", "render", "--side", side, "--width", "2000", "--height", "1720", "--quality", "high",
            "--zoom", "1.15", "-o", os.path.join(docs, f"{design.PROJECT}-3D-{side}.png"), pcb)
    run("pcb", "render", "--side", "top", "--width", "2000", "--height", "1500", "--quality", "high",
        "--rotate", "-45,0,30", "--zoom", "0.95", "-o", os.path.join(docs, f"{design.PROJECT}-3D-iso.png"), pcb)
    run("pcb", "export", "step", "--subst-models", "--force", "-o",
        os.path.join(docs, f"{design.PROJECT}.step"), pcb)
    print("exported:", sorted(os.listdir(prod)), sorted(os.listdir(docs)))


if __name__ == "__main__":
    main(sys.argv[1])
