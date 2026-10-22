# SPDX-FileCopyrightText: 2026 Emanuel Bachmann
# SPDX-License-Identifier: MIT
"""Autoroute Sensor-HAT.kicad_pcb with Freerouting, then refill the GND pours.

Run with KiCad's bundled Python:
  python3 -I route.py <project_dir> <freerouting.jar> <java> [passes]
"""
import json
import os
import random
import re
import shutil
import subprocess
import sys

import pcbnew

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import design  # noqa: E402
import placement  # noqa: E402
from gen_pcb import OX, OY  # noqa: E402

CLI = os.path.expanduser("~/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli")

# The DSN exporter turns every rule area into a full keepout. Areas that only
# forbid copper pours (BME688 island) or footprints (PoE headers) must stay
# routable, so they are stripped from the DSN by their first outline point.
TEMPLATE_POE_FIRST_POINT = (64.0, 12.14)


def soft_keepout_points():
    pts = [TEMPLATE_POE_FIRST_POINT]
    for _name, _layers, outline, forbidden in placement.KEEPOUTS:
        if "tracks" not in forbidden:
            pts.append(outline[0])
    return {(round((OX + x) * 1000), round(-(OY + y) * 1000)) for x, y in pts}


def strip_keepouts(dsn, first_points):
    text = open(dsn, encoding="utf-8").read()
    out, i, dropped = [], 0, 0
    while True:
        j = text.find("(keepout", i)
        if j < 0:
            out.append(text[i:])
            break
        depth, k = 0, j
        while True:
            if text[k] == "(":
                depth += 1
            elif text[k] == ")":
                depth -= 1
                if depth == 0:
                    break
            k += 1
        block = text[j:k + 1]
        m = re.search(r"polygon \S+ \S+\s+(-?[\d.]+)\s+(-?[\d.]+)", block)
        if m and (round(float(m.group(1))), round(float(m.group(2)))) in first_points:
            out.append(text[i:j])
            dropped += 1
        else:
            out.append(text[i:k + 1])
        i = k + 1
    with open(dsn, "w", encoding="utf-8") as f:
        f.write("".join(out))
    return dropped


def split_fixed_wires(dsn):
    """Write every fixed multi-point wire as single segments.

    KiCad exports a branching hand route as a polyline plus a wire that starts at one of
    its corners. Freerouting only joins traces at their end points, so it treats that
    branch as unconnected, keeps an "unrouted" connection and skips its optimizer.
    """
    pat = re.compile(r"^(\s*)\(wire \(path (\S+) (\S+)((?:\s+-?[\d.]+\s+-?[\d.]+)+)\)(.*\(type fix\)\))\s*$")
    out, split = [], 0
    for line in open(dsn, encoding="utf-8").read().splitlines():
        m = pat.match(line)
        if m:
            ind, layer, width, coords, rest = m.groups()
            v = coords.split()
            pts = [(v[i], v[i + 1]) for i in range(0, len(v), 2)]
            if len(pts) > 2:
                for a, b in zip(pts, pts[1:]):
                    out.append(f"{ind}(wire (path {layer} {width}  {a[0]} {a[1]}  {b[0]} {b[1]}){rest}")
                split += 1
                continue
        out.append(line)
    with open(dsn, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    return split


def shuffle_network(dsn, out, seed):
    """Copy of the DSN with the nets and their pins in a seeded random order.

    Freerouting is deterministic for a given file, so repeated attempts on the same DSN
    give identical results. The net order steers which connections it routes first.
    """
    lines = open(dsn, encoding="utf-8").read().split("\n")
    start = next(i for i, l in enumerate(lines) if l.startswith("  (network"))
    first_class = next(i for i in range(start, len(lines)) if lines[i].startswith("    (class"))
    nets, cur = [], None
    for l in lines[start + 1:first_class]:
        if l.startswith("    (net "):
            cur = [l]
            nets.append(cur)
        else:
            cur.append(l)
    rng = random.Random(seed)
    rng.shuffle(nets)
    body = []
    for blk in nets:
        text = "\n".join(blk)
        m = re.search(r"\(pins([^()]*)\)", text)
        if m:
            pins = m.group(1).split()
            rng.shuffle(pins)
            text = text[:m.start()] + "(pins " + " ".join(pins) + ")" + text[m.end():]
        body.append(text)
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines[:start + 1] + body + lines[first_class:]))


def strip_inner_planes(dsn, layers=("In2.Cu",)):
    """Drop the plane definitions of inner layers that Freerouting should route on.

    A +3V3 plane on In2 made Freerouting skip every +3V3 connection (it never fans out to it),
    so In2 is handed over as a routing layer and KiCad fills the leftover In2 area with +3V3
    afterwards. The solid GND plane on In1 stays a plane.
    """
    out, skip, dropped = [], False, 0
    for line in open(dsn, encoding="utf-8").read().split("\n"):
        if not skip and line.lstrip().startswith("(plane ") and any(f"(polygon {L} " in line for L in layers):
            skip = True
            dropped += 1
        if skip:
            if line.rstrip().endswith("))"):
                skip = False
            continue
        out.append(line)
    with open(dsn, "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    return dropped


def fill(board):
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())


def stitch_gnd(board, pitch=4.0, via_d=0.6, drill=0.3, extra=0.2, hole_gap=1.0):
    """Add GND vias wherever both GND pours overlap, then make sure every pour
    island that carries a GND pad reaches the other layer."""
    gnd = board.FindNet("/GND")
    pours = {z.GetLayer(): z for z in board.Zones()
             if not z.GetIsRuleArea() and z.GetNetCode() == gnd.GetNetCode() and z.GetLayer() in (pcbnew.F_Cu, pcbnew.B_Cu)}
    no_via = [z.Outline() for z in board.Zones() if z.GetIsRuleArea() and z.GetDoNotAllowVias()]
    courtyards = []
    for fp in board.GetFootprints():
        for layer in (pcbnew.F_CrtYd, pcbnew.B_CrtYd):
            cy = fp.GetCourtyard(layer)
            if cy.OutlineCount():
                courtyards.append(cy)
    # tracks on the inner routing layer (In2): stitching vias must keep clear of them as well
    inner_tracks = [t for t in board.GetTracks()
                    if t.Type() != pcbnew.PCB_VIA_T and t.GetLayer() not in (pcbnew.F_Cu, pcbnew.B_Cu)]
    inner_gap = pcbnew.FromMM(via_d / 2 + 0.25)

    def hits_inner(p):
        return any(t.HitTest(p, inner_gap) for t in inner_tracks)

    holes = [t.GetPosition() for t in board.GetTracks() if t.Type() == pcbnew.PCB_VIA_T]
    holes += [p.GetPosition() for fp in board.GetFootprints() for p in fp.Pads() if p.GetDrillSize().x > 0]
    r = via_d / 2 + extra
    ring = [(r * c, r * s) for c, s in ((1, 0), (0.707, 0.707), (0, 1), (-0.707, 0.707),
                                         (-1, 0), (-0.707, -0.707), (0, -1), (0.707, -0.707))]
    added = []

    def in_keepout(x, y):
        """True if any part of a via at (x, y) mm would touch a no-via rule area."""
        for dx, dy in [(0, 0)] + ring:
            q = pcbnew.VECTOR2I(pcbnew.FromMM(x + dx), pcbnew.FromMM(y + dy))
            if any(z.Contains(q) for z in no_via):
                return True
        return False

    def fills():
        return (pours[pcbnew.F_Cu].GetFilledPolysList(pcbnew.F_Cu),
                pours[pcbnew.B_Cu].GetFilledPolysList(pcbnew.B_Cu))

    def ok(x, y, ftop, fbot):
        p = pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y))
        for dx, dy in ring:
            q = pcbnew.VECTOR2I(pcbnew.FromMM(x + dx), pcbnew.FromMM(y + dy))
            if not (ftop.Contains(q) and fbot.Contains(q)):
                return False
        if any(c.Contains(p) for c in courtyards) or in_keepout(x, y) or hits_inner(p):
            return False
        lim = pcbnew.FromMM(hole_gap) ** 2
        return all((h.x - p.x) ** 2 + (h.y - p.y) ** 2 >= lim for h in holes)

    pad_boxes = []
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            bb = pad.GetBoundingBox()
            bb.Inflate(pcbnew.FromMM(via_d / 2 + 0.15))
            pad_boxes.append(bb)
    big_courtyards = [fp.GetCourtyard(pcbnew.F_CrtYd) for fp in board.GetFootprints()
                      if fp.GetReference()[0] in "UJ" and fp.GetCourtyard(pcbnew.F_CrtYd).OutlineCount()]
    ring_small = [(dx * (via_d / 2 + 0.05) / r, dy * (via_d / 2 + 0.05) / r) for dx, dy in ring]

    def ok_island(x, y, ftop, fbot):
        p = pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y))
        for dx, dy in ring_small:
            q = pcbnew.VECTOR2I(pcbnew.FromMM(x + dx), pcbnew.FromMM(y + dy))
            if not (ftop.Contains(q) and fbot.Contains(q)):
                return False
        if any(b.Contains(p) for b in pad_boxes) or any(c.Contains(p) for c in big_courtyards):
            return False
        if in_keepout(x, y) or hits_inner(p):
            return False
        lim = pcbnew.FromMM(0.8) ** 2
        return all((h.x - p.x) ** 2 + (h.y - p.y) ** 2 >= lim for h in holes)

    def add(x, y):
        v = pcbnew.PCB_VIA(board)
        v.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
        v.SetWidth(pcbnew.FromMM(via_d))
        v.SetDrill(pcbnew.FromMM(drill))
        v.SetNet(gnd)
        board.Add(v)
        holes.append(v.GetPosition())
        added.append(v)

    ftop, fbot = fills()
    steps = int(56 / pitch) + 1
    for i in range(int(65 / pitch) + 1):
        for j in range(steps):
            x, y = OX + 1.5 + i * pitch, OY + 1.5 + j * pitch
            if ok(x, y, ftop, fbot):
                add(x, y)
    fill(board)

    # Connectivity of the pour polygons: top and bottom polygons are joined by GND
    # vias and GND through-hole pads. Every group that is not part of the largest
    # one gets a via onto a polygon of the largest group.
    inner = [z for z in board.Zones() if not z.GetIsRuleArea() and z.GetNetCode() == gnd.GetNetCode()
             and z.GetLayer() not in (pcbnew.F_Cu, pcbnew.B_Cu)]

    def groups(ftop, fbot):
        nt = ftop.OutlineCount()
        polys = [(ftop, k) for k in range(nt)] + [(fbot, k) for k in range(fbot.OutlineCount())]
        for z in inner:                       # GND plane on an inner layer joins everything it touches
            fin = z.GetFilledPolysList(z.GetLayer())
            polys += [(fin, k) for k in range(fin.OutlineCount())]
        parent = list(range(len(polys)))

        def root(i):
            while parent[i] != i:
                parent[i] = parent[parent[i]]
                i = parent[i]
            return i

        links = [t.GetPosition() for t in board.GetTracks()
                 if t.Type() == pcbnew.PCB_VIA_T and t.GetNetCode() == gnd.GetNetCode()]
        links += [p.GetPosition() for fp in board.GetFootprints() for p in fp.Pads()
                  if p.GetDrillSize().x > 0 and p.GetNetCode() == gnd.GetNetCode()]
        for pos in links:
            on = [i for i, (poly, k) in enumerate(polys) if poly.Contains(pos, k)]
            for a, b in zip(on, on[1:]):
                parent[root(a)] = root(b)
        out = {}
        for i in range(len(polys)):
            out.setdefault(root(i), []).append(i)
        area = {g: sum(polys[i][0].Outline(polys[i][1]).Area() for i in m) for g, m in out.items()}
        main = max(area, key=area.get)
        return polys, out, main, root

    for _round in range(6):
        ftop, fbot = fills()
        polys, members, main, root = groups(ftop, fbot)
        main_set = set(members[main])
        fixed = 0
        for g, idx in members.items():
            if g == main:
                continue
            done = False
            for i in idx:
                poly, k = polys[i]
                bb = poly.Outline(k).BBox()
                x0, y0 = pcbnew.ToMM(bb.GetX()), pcbnew.ToMM(bb.GetY())
                w, h = pcbnew.ToMM(bb.GetWidth()), pcbnew.ToMM(bb.GetHeight())
                for a in range(int(w / 0.1) + 1):
                    for b in range(int(h / 0.1) + 1):
                        x, y = x0 + a * 0.1, y0 + b * 0.1
                        p = pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y))
                        if not poly.Contains(p, k) or not ok_island(x, y, ftop, fbot):
                            continue
                        other = [j for j in main_set if polys[j][0].Contains(p, polys[j][1])]
                        if other:
                            add(x, y)
                            done = True
                            break
                    if done:
                        break
                if done:
                    break
            fixed += done
        fill(board)
        if not fixed:
            break
    # redundancy: every pour polygon of useful size should have at least two links
    ftop, fbot = fills()
    gnd_links = [t.GetPosition() for t in board.GetTracks()
                 if t.Type() == pcbnew.PCB_VIA_T and t.GetNetCode() == gnd.GetNetCode()]
    gnd_links += [p.GetPosition() for fp in board.GetFootprints() for p in fp.Pads()
                  if p.GetDrillSize().x > 0 and p.GetNetCode() == gnd.GetNetCode()]
    for poly in (ftop, fbot):
        for k in range(poly.OutlineCount()):
            if poly.Outline(k).Area() < 1.5e12 or sum(1 for h in gnd_links if poly.Contains(h, k)) >= 2:
                continue
            bb = poly.Outline(k).BBox()
            x0, y0 = pcbnew.ToMM(bb.GetX()), pcbnew.ToMM(bb.GetY())
            w, h = pcbnew.ToMM(bb.GetWidth()), pcbnew.ToMM(bb.GetHeight())
            done = False
            for a in range(int(w / 0.2) + 1):
                for b in range(int(h / 0.2) + 1):
                    x, y = x0 + a * 0.2, y0 + b * 0.2
                    p = pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y))
                    if poly.Contains(p, k) and ok_island(x, y, ftop, fbot):
                        add(x, y)
                        gnd_links.append(p)
                        done = True
                        break
                if done:
                    break
    fill(board)
    ftop, fbot = fills()
    _polys, members, _main, _root = groups(ftop, fbot)
    print(f"GND pour groups after stitching: {len(members)} (1 = fully connected)")
    return len(added)


def drc_score(pcb):
    """(unconnected, errors, warnings) from kicad-cli DRC with schematic parity."""
    out = os.path.join(os.path.dirname(pcb), "build", "route", "drc.json")
    subprocess.run([CLI, "pcb", "drc", "--format", "json", "--severity-all", "--schematic-parity",
                    "-o", out, pcb], capture_output=True)
    d = json.load(open(out, encoding="utf-8"))
    items = d.get("violations", []) + d.get("schematic_parity", [])
    errors = sum(1 for v in items if v.get("severity") == "error")
    warnings = sum(1 for v in items if v.get("severity") == "warning")
    return len(d.get("unconnected_items", [])), errors, warnings


def main(project_dir, jar, java, passes="100", attempts="6"):
    pcb = os.path.join(project_dir, design.PROJECT + ".kicad_pcb")
    work = os.path.join(project_dir, "build", "route")
    os.makedirs(work, exist_ok=True)
    dsn = os.path.join(work, design.PROJECT + ".dsn")
    unrouted = os.path.join(work, "unrouted.kicad_pcb")
    shutil.copy(pcb, unrouted)

    board = pcbnew.LoadBoard(pcb)
    if not pcbnew.ExportSpecctraDSN(board, dsn):
        raise SystemExit("DSN export failed")
    print("soft keepouts removed from DSN:", strip_keepouts(dsn, soft_keepout_points()))
    print("fixed wires split into segments:", split_fixed_wires(dsn))
    print("inner planes handed to the router:", strip_inner_planes(dsn))

    best = None
    for n in range(int(attempts)):
        ses = os.path.join(work, f"attempt{n}.ses")
        if os.path.exists(ses):
            os.remove(ses)
        run_dsn = os.path.join(work, f"attempt{n}.dsn")
        shuffle_network(dsn, run_dsn, n + 1)
        cmd = [java, "-Djava.awt.headless=true", "-jar", jar, "--gui.enabled=false",
               "-de", run_dsn, "-do", ses, "-mp", str(passes), "-l", "en"]
        with open(os.path.join(work, f"freerouting{n}.log"), "w") as log:
            try:
                subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, check=False, timeout=1200, cwd=work)
            except subprocess.TimeoutExpired:
                print(f"attempt {n}: Freerouting timed out")
                continue
        if not os.path.exists(ses):
            print(f"attempt {n}: no .ses")
            continue
        shutil.copy(unrouted, pcb)          # fresh unrouted board next to the project file
        board = pcbnew.LoadBoard(pcb)
        if not pcbnew.ImportSpecctraSES(board, ses):
            print(f"attempt {n}: SES import failed")
            continue
        fill(board)
        stitched = stitch_gnd(board)
        pcbnew.SaveBoard(pcb, board, True)
        score = drc_score(pcb)
        vias = sum(1 for t in board.GetTracks() if t.Type() == pcbnew.PCB_VIA_T)
        print(f"attempt {n}: unconnected={score[0]} errors={score[1]} warnings={score[2]} "
              f"vias={vias} (stitching {stitched})")
        cand = os.path.join(work, f"attempt{n}.kicad_pcb")
        shutil.copy(pcb, cand)
        key = (score, vias)
        if best is None or key < best[0]:
            best = (key, cand, n)
        if score[0] == 0 and score[1] == 0 and score[2] == 0:
            break
    if best is None:
        raise SystemExit("no routing attempt succeeded")
    shutil.copy(best[1], pcb)
    print(f"best: attempt {best[2]} {best[0]}")


if __name__ == "__main__":
    main(*sys.argv[1:])
