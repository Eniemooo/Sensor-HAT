# SPDX-FileCopyrightText: 2026 Emanuel Bachmann
# SPDX-License-Identifier: MIT
"""Join GND copper that the pours left isolated after autorouting.

Signal tracks can box in a GND pad or fan-out via so that neither pour reaches it.
For every GND cluster that KiCad's connectivity does not join to the main one, a grid
search looks for a short GND tie (F.Cu or B.Cu) to main GND copper. If the tie only fits
after removing nearby signal tracks, those nets are ripped up, the tie is added (locked)
and Freerouting re-routes just the ripped nets with everything else fixed.
Run with KiCad's Python:  python3 -I repair_gnd.py <project_dir> <freerouting.jar> <java>
"""
import heapq
import itertools
import os
import re
import shutil
import subprocess
import sys

import pcbnew

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import design  # noqa: E402
import route  # noqa: E402
from sexpr import dump, find, find_all, parse  # noqa: E402

TIE_W = 0.3        # mm
CLEAR = 0.22       # mm to foreign copper (board minimum is 0.15)
EDGE = 0.35        # mm track edge to board edge
STEP = 0.1         # grid pitch, mm
WINDOW = 6.0       # search radius around the isolated copper, mm
NEAR = 3.0         # nets with copper this close to the isolated copper may be ripped up


def mm(v):
    return pcbnew.ToMM(v)


def iu(v):
    return pcbnew.FromMM(v)


def load_filled(pcb):
    board = pcbnew.LoadBoard(pcb)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    board.BuildConnectivity()
    return board


def gnd_items(board, gnd):
    items = [p for fp in board.GetFootprints() for p in fp.Pads() if p.GetNetCode() == gnd]
    return items + [t for t in board.GetTracks() if t.GetNetCode() == gnd]


def clusters(board, gnd):
    """GND pads/tracks/vias grouped by KiCad connectivity, largest first."""
    conn = board.GetConnectivity()
    items = gnd_items(board, gnd)
    by_id = {i.m_Uuid.AsString(): i for i in items}
    seen, out = set(), []
    for i in items:
        u = i.m_Uuid.AsString()
        if u in seen:
            continue
        ids = {x.m_Uuid.AsString() for x in conn.GetConnectedItems(i)} | {u}
        members = [by_id[k] for k in ids if k in by_id]
        seen.update(m.m_Uuid.AsString() for m in members)
        out.append(members)
    return sorted(out, key=len, reverse=True)


def label(item):
    if item.Type() == pcbnew.PCB_PAD_T:
        return f"{item.GetParentFootprint().GetReference()}.{item.GetNumber()}"
    p = item.GetPosition()
    return f"{'via' if item.Type() == pcbnew.PCB_VIA_T else 'track'}@({mm(p.x) - 100:.2f},{mm(p.y) - 44:.2f})"


def on_layer(item, layer):
    if item.Type() == pcbnew.PCB_VIA_T:
        return True
    if item.Type() == pcbnew.PCB_PAD_T:
        return item.IsOnLayer(layer)
    return item.GetLayer() == layer


class Grid:
    """Obstacle raster of one copper layer around the isolated copper."""

    def __init__(self, board, layer, cluster, main, gnd):
        self.layer = layer
        anchors = [i for i in cluster if on_layer(i, layer)]
        bb = anchors[0].GetBoundingBox()
        for i in anchors[1:]:
            bb.Merge(i.GetBoundingBox())
        x0, y0 = mm(bb.GetX()) - WINDOW, mm(bb.GetY()) - WINDOW
        self.x0, self.y0 = round(x0 / STEP) * STEP, round(y0 / STEP) * STEP
        self.nx = int((mm(bb.GetWidth()) + 2 * WINDOW) / STEP) + 1
        self.ny = int((mm(bb.GetHeight()) + 2 * WINDOW) / STEP) + 1
        n = self.nx * self.ny
        self.hard = bytearray(n)
        self.soft = {}
        self.own = bytearray(n)
        self.target = bytearray(n)
        acc = TIE_W / 2 + CLEAR + 0.08  # margin for diagonal steps between cell centres

        outline = pcbnew.SHAPE_POLY_SET()
        board.GetBoardPolygonOutlines(outline, False)
        r = TIE_W / 2 + EDGE
        ring = [(r, 0), (-r, 0), (0, r), (0, -r), (0.7 * r, 0.7 * r), (-0.7 * r, 0.7 * r),
                (0.7 * r, -0.7 * r), (-0.7 * r, -0.7 * r), (0, 0)]
        keep = [z.Outline() for z in board.Zones() if z.GetIsRuleArea() and z.GetDoNotAllowTracks()
                and z.IsOnLayer(layer)]
        rk = TIE_W / 2 + 0.15
        ring_k = [(rk, 0), (-rk, 0), (0, rk), (0, -rk), (0.7 * rk, 0.7 * rk), (-0.7 * rk, 0.7 * rk),
                  (0.7 * rk, -0.7 * rk), (-0.7 * rk, -0.7 * rk), (0, 0)]
        for c in range(n):
            x, y = self.xy(c)
            if not all(outline.Contains(pcbnew.VECTOR2I(iu(x + dx), iu(y + dy))) for dx, dy in ring):
                self.hard[c] = 1
            elif any(k.Contains(pcbnew.VECTOR2I(iu(x + dx), iu(y + dy))) for k in keep for dx, dy in ring_k):
                self.hard[c] = 1

        locked_nets = {t.GetNetCode() for t in board.GetTracks() if t.IsLocked()}
        own_ids = {i.m_Uuid.AsString() for i in cluster}
        main_ids = {i.m_Uuid.AsString() for i in main}
        for fp in board.GetFootprints():
            for p in fp.Pads():
                if p.GetNetCode() == gnd and p.GetAttribute() != pcbnew.PAD_ATTRIB_NPTH:
                    if not p.IsOnLayer(layer):
                        continue
                    u = p.m_Uuid.AsString()
                    if u in own_ids:
                        self.mark(p, 0, self.own)
                    elif u in main_ids:
                        self.mark(p, 0, self.target)
                    continue
                if p.IsOnLayer(layer) or p.GetDrillSize().x > 0:
                    self.mark(p, acc, self.hard)
        for t in board.GetTracks():
            if not on_layer(t, layer):
                continue
            if t.GetNetCode() == gnd:
                u = t.m_Uuid.AsString()
                if t.Type() != pcbnew.PCB_VIA_T:
                    continue          # ties start and end on pads or vias only
                if u in own_ids:
                    self.mark(t, 0, self.own)
                elif u in main_ids:
                    self.mark(t, 0, self.target)
                continue
            if t.IsLocked() or t.GetNetCode() in locked_nets:
                self.mark(t, acc, self.hard)
            else:
                self.mark(t, acc, None, t.GetNetCode())

    def xy(self, c):
        return self.x0 + (c % self.nx) * STEP, self.y0 + (c // self.nx) * STEP

    def mark(self, item, acc, arr, net=None):
        bb = item.GetBoundingBox()
        a = acc + STEP
        i0 = max(0, int((mm(bb.GetX()) - a - self.x0) / STEP))
        i1 = min(self.nx - 1, int((mm(bb.GetRight()) + a - self.x0) / STEP) + 1)
        j0 = max(0, int((mm(bb.GetY()) - a - self.y0) / STEP))
        j1 = min(self.ny - 1, int((mm(bb.GetBottom()) + a - self.y0) / STEP) + 1)
        tol = iu(acc)
        for j in range(j0, j1 + 1):
            for i in range(i0, i1 + 1):
                c = j * self.nx + i
                x, y = self.xy(c)
                if not item.HitTest(pcbnew.VECTOR2I(iu(x), iu(y)), tol):
                    continue
                if arr is not None:
                    arr[c] = 1
                else:
                    self.soft.setdefault(c, set()).add(net)

    def soft_nets(self, near_cells):
        out = set()
        for c in near_cells:
            out |= self.soft.get(c, set())
        return out

    def search(self, ripped):
        """Shortest free path from own copper to main GND copper, or None."""
        def free(c):
            if self.own[c] or self.target[c]:
                return True
            if self.hard[c]:
                return False
            s = self.soft.get(c)
            return s is None or s <= ripped

        dist, prev, heap = {}, {}, []
        for c in range(len(self.own)):
            if self.own[c]:
                dist[c] = 0.0
                heapq.heappush(heap, (0.0, c))
        nx = self.nx
        moves = [(1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0),
                 (1, 1, 1.414), (1, -1, 1.414), (-1, 1, 1.414), (-1, -1, 1.414)]
        while heap:
            d, c = heapq.heappop(heap)
            if d > dist.get(c, 1e9):
                continue
            if self.target[c]:
                path = [c]
                while path[-1] in prev:
                    path.append(prev[path[-1]])
                return d * STEP, path[::-1]
            i, j = c % nx, c // nx
            for di, dj, w in moves:
                ii, jj = i + di, j + dj
                if not (0 <= ii < nx and 0 <= jj < self.ny):
                    continue
                q = jj * nx + ii
                if not free(q):
                    continue
                if di and dj and not (free(j * nx + ii) or free(jj * nx + i)):
                    continue
                nd = d + w
                if nd < dist.get(q, 1e9):
                    dist[q], prev[q] = nd, c
                    heapq.heappush(heap, (nd, q))
        return None

    def corners(self, path):
        """Path cells -> polyline corner points (mm). Leading/trailing cells inside copper are dropped."""
        while len(path) > 2 and self.own[path[1]]:
            path = path[1:]
        while len(path) > 2 and self.target[path[-2]]:
            path = path[:-1]
        pts = [self.xy(c) for c in path]
        out = [pts[0]]
        for a, b, c in zip(pts, pts[1:], pts[2:]):
            if abs((b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])) > 1e-9:
                out.append(b)
        out.append(pts[-1])
        return out


def net_track_length(board, code):
    return sum(mm(t.GetLength()) for t in board.GetTracks()
               if t.GetNetCode() == code and t.Type() != pcbnew.PCB_VIA_T)


def plan(board, cluster, main, gnd):
    """Cheapest (rip-up set, layer, polyline) that joins the cluster to main GND copper."""
    best = None
    for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
        if not any(on_layer(i, layer) for i in cluster):
            continue
        g = Grid(board, layer, cluster, main, gnd)
        own = [c for c in range(len(g.own)) if g.own[c]]
        near = set()
        reach = int(NEAR / STEP)
        for c in own[::3]:
            i, j = c % g.nx, c // g.nx
            for jj in range(max(0, j - reach), min(g.ny, j + reach + 1), 2):
                for ii in range(max(0, i - reach), min(g.nx, i + reach + 1), 2):
                    near.add(jj * g.nx + ii)
        nets = sorted(g.soft_nets(near))
        for size in range(0, 3):
            found = []
            for combo in itertools.combinations(nets, size):
                res = g.search(set(combo))
                if res:
                    cost = sum(net_track_length(board, n) for n in combo)
                    found.append((cost + res[0], combo, layer, g.corners(res[1])))
            if found:
                cand = min(found, key=lambda f: f[0])
                key = (size, cand[0])
                if best is None or key < best[0]:
                    best = (key, cand[1], cand[2], cand[3])
                break
    return best


def rip(pcb_in, pcb_out, netnames):
    """Copy the board without the (unlocked) tracks and vias of the given nets."""
    tree = parse(open(pcb_in, encoding="utf-8").read())
    keep, n = [], 0
    for x in tree:
        if isinstance(x, list) and x and x[0] in ("segment", "via", "arc"):
            net, locked = find(x, "net"), find(x, "locked")
            if net and str(net[1]) in netnames and not (locked and locked[1] == "yes"):
                n += 1
                continue
        keep.append(x)
    tree[:] = keep
    with open(pcb_out, "w", encoding="utf-8") as f:
        f.write(dump(tree) + "\n")
    return n


def add_track(board, net, layer, a, b, width, locked=False):
    t = pcbnew.PCB_TRACK(board)
    t.SetStart(pcbnew.VECTOR2I(iu(a[0]), iu(a[1])))
    t.SetEnd(pcbnew.VECTOR2I(iu(b[0]), iu(b[1])))
    t.SetWidth(iu(width))
    t.SetLayer(layer)
    t.SetNet(net)
    t.SetLocked(locked)
    board.Add(t)


def add_via(board, net, pos, size, drill):
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(pcbnew.VECTOR2I(iu(pos[0]), iu(pos[1])))
    v.SetWidth(iu(size))
    v.SetDrill(iu(drill))
    v.SetNet(net)
    board.Add(v)


def reroute(work, pcb_ripped, netnames, jar, java):
    """Route only the ripped nets: everything else goes to Freerouting as fixed wiring."""
    board = pcbnew.LoadBoard(pcb_ripped)
    for t in board.GetTracks():
        t.SetLocked(True)
    dsn = os.path.join(work, "repair.dsn")
    ses = os.path.join(work, "repair.ses")
    if os.path.exists(ses):
        os.remove(ses)
    if not pcbnew.ExportSpecctraDSN(board, dsn):
        raise SystemExit("DSN export failed")
    route.strip_keepouts(dsn, route.soft_keepout_points())
    route.split_fixed_wires(dsn)
    route.strip_inner_planes(dsn)
    with open(os.path.join(work, "freerouting-repair.log"), "w") as log:
        subprocess.run([java, "-Djava.awt.headless=true", "-jar", jar, "--gui.enabled=false",
                        "-de", dsn, "-do", ses, "-mp", "30", "-l", "en"],
                       stdout=log, stderr=subprocess.STDOUT, check=False, timeout=1200, cwd=work)
    if not os.path.exists(ses):
        return None
    tree = parse(open(ses, encoding="utf-8").read())
    res = find(find(tree, "routes"), "resolution")
    scale = {"um": 1e-3, "mm": 1.0, "mil": 0.0254}[str(res[1])] / float(res[2])
    wires, vias = [], []
    for net in find_all(find(find(tree, "routes"), "network_out"), "net"):
        name = str(net[1])
        if name not in netnames:
            continue
        for w in find_all(net, "wire"):
            path = find(w, "path")
            layer, width = str(path[1]), float(path[2]) * scale
            xy = [float(v) * scale for v in path[3:]]
            pts = [(xy[k], -xy[k + 1]) for k in range(0, len(xy) - 1, 2)]
            for a, b in zip(pts, pts[1:]):
                wires.append((name, layer, a, b, width))
        for v in find_all(net, "via"):
            m = re.search(r"_(\d+):(\d+)_um", str(v[1]))
            size, drill = (int(m.group(1)) / 1000, int(m.group(2)) / 1000) if m else (0.6, 0.3)
            vias.append((name, (float(v[2]) * scale, -float(v[3]) * scale), size, drill))
    return wires, vias


def main(project_dir, jar, java):
    pcb = os.path.join(project_dir, design.PROJECT + ".kicad_pcb")
    work = os.path.join(project_dir, "build", "route")
    os.makedirs(work, exist_ok=True)
    for attempt in range(6):
        board = load_filled(pcb)
        gnd = board.FindNet("/GND").GetNetCode()
        cl = clusters(board, gnd)
        if len(cl) == 1:
            print("GND fully connected")
            return
        main_cl, iso = cl[0], cl[1]
        print(f"isolated GND copper: {[label(i) for i in iso]}")
        p = plan(board, iso, main_cl, gnd)
        if p is None:
            print("  no tie found - leaving it for manual work")
            return
        _key, combo, layer, pts = p
        netnames = {board.FindNet(n).GetNetname() for n in combo}
        print(f"  tie on {pcbnew.LayerName(layer)}, {len(pts) - 1} segment(s); rip up: {sorted(netnames) or 'nothing'}")
        ripped = os.path.join(work, "repair-ripped.kicad_pcb")
        print("  removed items:", rip(pcb, ripped, netnames))
        board = pcbnew.LoadBoard(ripped)
        net = board.FindNet("/GND")
        for a, b in zip(pts, pts[1:]):
            add_track(board, net, layer, a, b, TIE_W, locked=True)
        pcbnew.SaveBoard(ripped, board, True)
        if netnames:
            got = reroute(work, ripped, netnames, jar, java)
            if got is None:
                print("  Freerouting produced no session - stop")
                return
            wires, vias = got
            board = pcbnew.LoadBoard(ripped)
            for name, lname, a, b, w in wires:
                add_track(board, board.FindNet(name), board.GetLayerID(lname), a, b, w)
            for name, pos, size, drill in vias:
                add_via(board, board.FindNet(name), pos, size, drill)
            print(f"  re-routed: {len(wires)} segments, {len(vias)} vias")
            pcbnew.ZONE_FILLER(board).Fill(board.Zones())
            pcbnew.SaveBoard(ripped, board, True)
        before = os.path.join(work, "repair-before.kicad_pcb")
        shutil.copy(pcb, before)
        score_before = route.drc_score(pcb)
        shutil.copy(ripped, pcb)
        score = route.drc_score(pcb)
        print("  DRC (unconnected, errors, warnings):", score_before, "->", score)
        # a repair must remove unconnected items without adding errors or many warnings
        if not (score[0] < score_before[0] and score[1] <= score_before[1] and score[2] <= score_before[2] + 2):
            shutil.copy(before, pcb)       # the repair made nothing better: keep the old board
            print("  no improvement - reverted, stopping")
            return
    print("GND repair: attempts exhausted")


if __name__ == "__main__":
    main(*sys.argv[1:])
