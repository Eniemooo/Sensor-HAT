# SPDX-FileCopyrightText: 2026 Emanuel Bachmann
# SPDX-License-Identifier: MIT
"""Build Sensor-HAT.kicad_pcb from KiCad's RaspberryPi-HAT template + design.py + placement.py.

Run with KiCad's bundled Python:
  .../KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 -I gen_pcb.py <project_dir>
"""
import os
import sys
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pcbnew  # noqa: E402

import design  # noqa: E402
import placement  # noqa: E402
import sexpr  # noqa: E402
import kicadlib  # noqa: E402

KICAD_SHARE = os.path.expanduser("~/Applications/KiCad/KiCad.app/Contents/SharedSupport")
TEMPLATE = os.path.join(KICAD_SHARE, "template", "RaspberryPi-HAT", "RaspberryPi-HAT.kicad_pcb")
OX, OY = 100.0, 44.0          # template board origin (top-left corner)
W, H, RC = 65.0, 56.0, 3.0    # template outline (HAT), corner radius


def mm(x, y):
    return pcbnew.VECTOR2I(pcbnew.FromMM(OX + x), pcbnew.FromMM(OY + y))


def sym_uuid(ref):
    return str(uuid.uuid5(design.NAMESPACE, "sym-" + ref))


def lib_path(lib, project_dir):
    if lib == "SensorHAT":
        return os.path.join(project_dir, "lib", "SensorHAT.pretty")
    return os.path.join(KICAD_SHARE, "footprints", lib + ".pretty")


def add_line(board, layer, a, b, width=0.1):
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(mm(*a))
    s.SetEnd(mm(*b))
    s.SetLayer(layer)
    s.SetWidth(pcbnew.FromMM(width))
    board.Add(s)


def add_logo_placeholders(board):
    """AISLER logo replacement: four separate silkscreen lines per rectangle (placement.LOGO_PLACEHOLDERS)."""
    for side, x0, y0, x1, y1 in placement.LOGO_PLACEHOLDERS:
        layer = {"F": pcbnew.F_SilkS, "B": pcbnew.B_SilkS}[side]
        corners = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        for a, b in zip(corners, corners[1:] + corners[:1]):
            add_line(board, layer, a, b, width=placement.LOGO_LINE_WIDTH)


def add_arc(board, layer, start, mid, end, width=0.1):
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_ARC)
    s.SetArcGeometry(mm(*start), mm(*mid), mm(*end))
    s.SetLayer(layer)
    s.SetWidth(pcbnew.FromMM(width))
    board.Add(s)


def add_rect(board, layer, x0, y0, x1, y1, width=0.1):
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_RECT)
    s.SetStart(mm(x0, y0))
    s.SetEnd(mm(x1, y1))
    s.SetLayer(layer)
    s.SetWidth(pcbnew.FromMM(width))
    board.Add(s)


def add_text(board, text, x, y, size=1.0, layer=pcbnew.F_SilkS, angle=0, bold=False, justify=None):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(text)
    t.SetPosition(mm(x, y))
    t.SetLayer(layer)
    t.SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(size), pcbnew.FromMM(size)))
    t.SetTextThickness(pcbnew.FromMM(0.15 if size < 1.2 else 0.2))
    t.SetBold(bold)
    t.SetTextAngleDegrees(angle)
    if justify == "left":
        t.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_LEFT)
    elif justify == "right":
        t.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_RIGHT)
    if layer == pcbnew.B_SilkS:
        t.SetMirrored(True)
    board.Add(t)


def clean_template(path):
    """Copy of the template without its outline (optional camera/display cutouts), nets and groups.

    Done on the S-expression text: removing items through the SWIG API corrupts
    its type table (footprints come back as bare SwigPyObject).
    """
    tree = sexpr.parse(open(TEMPLATE, encoding="utf-8").read())

    def drop(x):
        if not isinstance(x, list) or not x:
            return False
        if x[0] in ("net", "group"):
            return True
        if x[0] == "footprint":   # J1 is reloaded from the library so it matches it exactly
            ref = [p for p in sexpr.find_all(x, "property") if p[1] == "Reference"]
            if ref and ref[0][2] == "J1":
                return True
        if str(x[0]).startswith("gr_"):
            layer = sexpr.find(x, "layer")
            if layer and layer[1] == "Edge.Cuts":
                return True
            if x[0] == "gr_text" and "OPTIONAL" in x[1]:
                return True
        return False

    tree[:] = [x for x in tree if not drop(x)]
    for pad in sexpr.walk(tree, "pad"):
        pad[:] = [x for x in pad if not (isinstance(x, list) and x and x[0] == "net")]
    with open(path, "w", encoding="utf-8") as f:
        f.write(sexpr.dump(tree) + "\n")


def outline(board):
    """Plain rounded-rectangle HAT outline plus the routed isolation slots."""
    e = pcbnew.Edge_Cuts
    add_line(board, e, (RC, 0), (W - RC, 0))
    add_line(board, e, (W, RC), (W, H - RC))
    add_line(board, e, (W - RC, H), (RC, H))
    add_line(board, e, (0, H - RC), (0, RC))
    k = RC * (1 - 0.70710678)
    add_arc(board, e, (0, RC), (k, k), (RC, 0))
    add_arc(board, e, (W - RC, 0), (W - k, k), (W, RC))
    add_arc(board, e, (W, H - RC), (W - k, H - k), (W - RC, H))
    add_arc(board, e, (RC, H), (k, H - k), (0, H - RC))
    for p0, p1, p2 in placement.L_SLOTS:
        add_l_slot(board, p0, p1, p2, placement.SLOT_W / 2)


def add_l_slot(board, p0, p1, p2, h):
    """L-shaped routed slot along the centreline p0 -> p1 (corner) -> p2, half-width h.

    Round caps at both ends and a round outer corner, i.e. exactly what a
    router bit of diameter 2h leaves behind.
    """
    def unit(a, b):
        dx, dy = b[0] - a[0], b[1] - a[1]
        n = (dx * dx + dy * dy) ** 0.5
        return dx / n, dy / n

    def pt(base, *terms):
        x, y = base
        for (vx, vy), k in terms:
            x, y = x + vx * k, y + vy * k
        return (x, y)

    d1, d2 = unit(p0, p1), unit(p1, p2)
    s2 = 0.70710678
    corner_dir = ((d1[0] - d2[0]) * s2, (d1[1] - d2[1]) * s2)
    e = pcbnew.Edge_Cuts
    a = pt(p0, (d2, -h))
    b = pt(p1, (d2, -h))
    c = pt(p1, (d1, h))
    d = pt(p2, (d1, h))
    f = pt(p2, (d1, -h))
    g = pt(p1, (d2, h), (d1, -h))
    k = pt(p0, (d2, h))
    add_line(board, e, a, b)
    add_arc(board, e, b, pt(p1, (corner_dir, h)), c)
    add_line(board, e, c, d)
    add_arc(board, e, d, pt(p2, (d2, h)), f)
    add_line(board, e, f, g)
    add_line(board, e, g, k)
    add_arc(board, e, k, pt(p0, (d1, -h)), a)


def add_slot(board, x0, y0, x1, y1):
    """Obround routed slot (JLC needs rounded ends)."""
    e = pcbnew.Edge_Cuts
    if x1 - x0 >= y1 - y0:
        r = (y1 - y0) / 2
        cy = (y0 + y1) / 2
        add_line(board, e, (x0 + r, y0), (x1 - r, y0))
        add_line(board, e, (x1 - r, y1), (x0 + r, y1))
        add_arc(board, e, (x0 + r, y1), (x0, cy), (x0 + r, y0))
        add_arc(board, e, (x1 - r, y0), (x1, cy), (x1 - r, y1))
    else:
        r = (x1 - x0) / 2
        cx = (x0 + x1) / 2
        add_line(board, e, (x0, y0 + r), (x0, y1 - r))
        add_line(board, e, (x1, y1 - r), (x1, y0 + r))
        add_arc(board, e, (x0, y1 - r), (cx, y1), (x1, y1 - r))
        add_arc(board, e, (x1, y0 + r), (cx, y0), (x0, y0 + r))


LAYERS = {"F.Cu": pcbnew.F_Cu, "In1.Cu": pcbnew.In1_Cu, "In2.Cu": pcbnew.In2_Cu, "B.Cu": pcbnew.B_Cu}


def rule_area(board, name, layers, pts, forbidden):
    z = pcbnew.ZONE(board)
    ls = pcbnew.LSET()
    for layer in layers:
        ls.AddLayer(LAYERS[layer])
    z.SetLayerSet(ls)
    z.SetIsRuleArea(True)
    z.SetDoNotAllowZoneFills("zones" in forbidden)
    z.SetDoNotAllowTracks("tracks" in forbidden)
    z.SetDoNotAllowVias("vias" in forbidden)
    z.SetDoNotAllowPads(False)
    z.SetDoNotAllowFootprints("footprints" in forbidden)
    z.SetZoneName(name)
    ol = z.Outline()
    ol.NewOutline()
    for x, y in pts:
        p = mm(x, y)
        ol.Append(p.x, p.y)
    board.Add(z)


def zone(board, net, layer, pts, name="", priority=0, clearance=0.3):
    z = pcbnew.ZONE(board)
    z.SetLayer(layer)
    z.SetNet(net)
    z.SetLocalClearance(pcbnew.FromMM(clearance))
    z.SetMinThickness(pcbnew.FromMM(0.25))
    z.SetThermalReliefGap(pcbnew.FromMM(0.3))
    z.SetThermalReliefSpokeWidth(pcbnew.FromMM(0.5))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THT_THERMAL)  # solid SMD, spokes on THT for hand soldering
    z.SetAssignedPriority(priority)
    z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    if name:
        z.SetZoneName(name)
    ol = z.Outline()
    ol.NewOutline()
    for x, y in pts:
        p = mm(x, y)
        ol.Append(p.x, p.y)
    board.Add(z)
    return z


def orient_j1(fp):
    """Rotate the bottom-side 2x20 socket until pin 1 is at (8.37, 4.77) and pin 2 at (8.37, 2.23)."""
    pads = {p.GetNumber(): p for p in fp.Pads()}
    target1, target2 = mm(8.37, 4.77), mm(8.37, 2.23)
    for rot in (-90, 90, 0, 180):
        fp.SetOrientationDegrees(rot)
        d = pads["1"].GetPosition()
        fp.SetPosition(pcbnew.VECTOR2I(fp.GetPosition().x + target1.x - d.x, fp.GetPosition().y + target1.y - d.y))
        p2 = pads["2"].GetPosition()
        if abs(p2.x - target2.x) < 1000 and abs(p2.y - target2.y) < 1000:
            return
    raise SystemExit("J1: no orientation puts pin 1/2 at the HAT positions")


def add_via(board, net, x, y, d=0.6, drill=0.3, locked=False):
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(mm(x, y))
    v.SetWidth(pcbnew.FromMM(d))
    v.SetDrill(pcbnew.FromMM(drill))
    v.SetNet(net)
    v.SetLocked(locked)
    board.Add(v)
    return v


def fanout_gnd(board, gnd, via_d=0.6, track_w=0.3, clearance=0.25):
    """Give every GND SMD pad its own short track + via before autorouting.

    Freerouting otherwise assumes such pads reach the GND plane and leaves
    pads that sit in tightly surrounded pour fragments unconnected.
    """
    import math
    pads = [p for fp in board.GetFootprints() for p in fp.Pads()]
    vias = [t for t in board.GetTracks() if t.Type() == pcbnew.PCB_VIA_T]
    tracks = [t for t in board.GetTracks() if t.Type() != pcbnew.PCB_VIA_T]
    keep = [z.Outline() for z in board.Zones() if z.GetIsRuleArea() and z.GetDoNotAllowVias()]
    edge = board.GetBoardEdgesBoundingBox()
    r = via_d / 2

    def blocked(x, y, own_pad, acc):
        p = mm(x, y)
        a = pcbnew.FromMM(acc)
        for q in pads:
            if q == own_pad:  # SWIG proxies: identity differs, equality compares the object
                continue
            same = q.GetNetCode() == gnd.GetNetCode()
            if q.HitTest(p, a if not same else pcbnew.FromMM(acc - clearance + 0.1)):
                return True
        for t in tracks:
            if t.GetNetCode() != gnd.GetNetCode() and t.HitTest(p, a + pcbnew.FromMM(t.GetWidth() / 2e6)):
                return True
        return False

    def via_ok(x, y, own_pad):
        if blocked(x, y, own_pad, r + clearance):
            return False
        p = mm(x, y)
        for dx, dy in ((0, 0), (r, 0), (-r, 0), (0, r), (0, -r)):   # whole via, not just its centre
            if any(k.Contains(mm(x + dx, y + dy)) for k in keep):
                return False
        for fp in board.GetFootprints():
            cy = fp.GetCourtyard(pcbnew.F_CrtYd)
            if fp.GetReference()[0] in "UJ" and cy.OutlineCount() and cy.Contains(p):
                return False
        lim = pcbnew.FromMM(via_d + 0.3) ** 2
        if any((v.GetPosition().x - p.x) ** 2 + (v.GetPosition().y - p.y) ** 2 < lim for v in vias):
            return False
        m = pcbnew.FromMM(1.0)
        return (edge.GetLeft() + m < p.x < edge.GetRight() - m and edge.GetTop() + m < p.y < edge.GetBottom() - m)

    def path_ok(x0, y0, x1, y1, own_pad):
        n = 12
        for i in range(1, n + 1):
            x, y = x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n
            if blocked(x, y, own_pad, track_w / 2 + clearance):
                return False
        return True

    added = 0
    for fp in board.GetFootprints():
        if fp.GetReference() in placement.NO_FANOUT or fp.IsFlipped():
            continue
        cx, cy = pcbnew.ToMM(fp.GetPosition().x) - OX, pcbnew.ToMM(fp.GetPosition().y) - OY
        for pad in fp.Pads():
            if pad.GetNetCode() != gnd.GetNetCode() or pad.GetDrillSize().x > 0:
                continue
            if pad.GetSize().x > pcbnew.FromMM(3):   # big centre pads sit in the pour anyway
                continue
            px, py = pcbnew.ToMM(pad.GetPosition().x) - OX, pcbnew.ToMM(pad.GetPosition().y) - OY
            base = math.atan2(py - cy, px - cx) if (px, py) != (cx, cy) else 0.0
            done = False
            # keep the whole via (and its drill) clear of the pad's mask opening
            half = max(pcbnew.ToMM(pad.GetSize().x), pcbnew.ToMM(pad.GetSize().y)) / 2
            dmin = half + r + 0.15
            for dist in [d for d in (1.1, 1.4, 1.8, 2.2, 2.6) if d >= dmin] or [dmin]:
                for da in (0, 30, -30, 60, -60, 90, -90, 135, -135, 180):
                    a = base + math.radians(da)
                    vx, vy = px + dist * math.cos(a), py + dist * math.sin(a)
                    if via_ok(vx, vy, pad) and path_ok(px, py, vx, vy, pad):
                        t = pcbnew.PCB_TRACK(board)
                        t.SetStart(mm(px, py))
                        t.SetEnd(mm(vx, vy))
                        t.SetWidth(pcbnew.FromMM(track_w))
                        t.SetLayer(pcbnew.F_Cu)
                        t.SetNet(gnd)
                        t.SetLocked(True)
                        board.Add(t)
                        tracks.append(t)
                        vias.append(add_via(board, gnd, vx, vy, via_d, locked=True))
                        added += 1
                        done = True
                        break
                if done:
                    break
            if not done:
                print(f"  no fan-out room for {fp.GetReference()}.{pad.GetNumber()}")
    return added


def main(project_dir):
    tmp = os.path.join(project_dir, ".template-clean.kicad_pcb")
    clean_template(tmp)
    board = pcbnew.LoadBoard(tmp)
    os.remove(tmp)
    # 4 layers: F.Cu signals, In1 solid GND plane, In2 signals + 3V3 fill, B.Cu signals.
    # (route.py hands In2 to Freerouting as a routing layer; In1 stays a plane.)
    board.SetCopperLayerCount(4)
    board.SetLayerType(pcbnew.In1_Cu, pcbnew.LT_POWER)
    board.SetLayerType(pcbnew.In2_Cu, pcbnew.LT_MIXED)
    outline(board)

    nets = {}
    for n in sorted({n for part in design.PARTS for n in part.get("pins", {}).values()}):
        ni = pcbnew.NETINFO_ITEM(board, "/" + n)  # schematic local labels -> /NAME
        board.Add(ni)
        nets[n] = ni

    existing = {fp.GetReference(): fp for fp in board.GetFootprints()}
    for part in design.PARTS:
        ref = part["ref"]
        if ref.startswith("#"):
            continue
        lib, name = part["fp"].split(":", 1)
        if ref in existing:
            fp = existing[ref]
        else:
            fp = pcbnew.FootprintLoad(lib_path(lib, project_dir), name)
            if fp is None:
                raise SystemExit(f"{ref}: footprint {part['fp']} not found")
            board.Add(fp)
        fp.SetFPID(pcbnew.LIB_ID(lib, name))
        fp.SetReference(ref)
        fp.SetValue(part["value"])
        fp.SetPath(pcbnew.KIID_PATH("/" + sym_uuid(ref)))
        fp.SetSheetname("/")
        fp.SetSheetfile(design.PROJECT + ".kicad_sch")
        fp.SetField("Datasheet", part.get("datasheet", ""))
        fp.SetField("Description", part.get("desc", ""))
        for key in ("LCSC", "MPN", "Manufacturer"):
            if part.get(key):
                fp.SetField(key, part[key])
                f = fp.GetField(key)
                f.SetVisible(False)
                f.SetLayer(pcbnew.F_Fab)
        if part.get("no_bom"):
            fp.SetExcludedFromBOM(True)
            fp.SetExcludedFromPosFiles(True)
        if part.get("dnp"):
            fp.SetDNP(True)

        if ref not in placement.PLACE:
            raise SystemExit(f"{ref}: no placement")
        x, y, rot, side = placement.PLACE[ref]
        if ref not in existing:
            if side == "B" and not fp.IsFlipped():
                fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_TOP_BOTTOM)
            fp.SetPosition(mm(x, y))
            fp.SetOrientationDegrees(rot)

        pin_nets = dict(part.get("pins", {}))
        # unconnected symbol pins get KiCad's 'unconnected-(...)' nets so schematic parity holds
        for num, (_x, _y, _a, pname, ptype) in kicadlib.pins(kicadlib.load_symbol(part["sym"])).items():
            if num not in pin_nets:
                # KiCad drops the pin name when it is empty or just repeats the number
                label = "" if pname in ("", "~", num) else pname + "-"
                n = f"unconnected-({ref}-{label}Pad{num})"
                if n not in nets:
                    nets[n] = pcbnew.NETINFO_ITEM(board, n)
                    board.Add(nets[n])
                pin_nets[num] = n
        for pad in fp.Pads():
            num = pad.GetNumber()
            n = pin_nets.get(num)
            if n:
                pad.SetNet(nets[n])
            elif num and pad.GetAttribute() != pcbnew.PAD_ATTRIB_NPTH:
                pad.SetNetCode(0)
        if ref == "J1":
            orient_j1(fp)
        missing = set(pin_nets) - {p.GetNumber() for p in fp.Pads()}
        if missing:
            raise SystemExit(f"{ref}: pins {sorted(missing)} have no pad in {part['fp']}")

        ref_field = fp.Reference()
        rx, ry, rrot = placement.REF_POS.get(ref, (None, None, None))
        if rx is not None:
            ref_field.SetPosition(mm(rx, ry))
            ref_field.SetTextAngleDegrees(rrot)
        # references live on the fab layer (assembly drawing); silkscreen only carries labels
        ref_field.SetLayer(pcbnew.B_Fab if fp.IsFlipped() else pcbnew.F_Fab)
        ref_field.SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(0.8), pcbnew.FromMM(0.8)))
        ref_field.SetTextThickness(pcbnew.FromMM(0.15))
        fp.Value().SetVisible(False)

    # hand-routed, locked island traces (the autorouter keeps them)
    hand_tracks = [(placement.ISLAND_ORIGIN, t) for t in placement.ISLAND_TRACKS]
    hand_tracks += [(placement.SCD41_ORIGIN, t) for t in placement.SCD41_TRACKS]
    hand_tracks += [((0.0, 0.0), t) for t in placement.J1_GND_TRACKS]
    for (ox, oy), (net, width, layer, pts) in hand_tracks:
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            t = pcbnew.PCB_TRACK(board)
            t.SetStart(mm(ox + x0, oy + y0))
            t.SetEnd(mm(ox + x1, oy + y1))
            t.SetWidth(pcbnew.FromMM(width))
            t.SetLayer(LAYERS[layer])
            t.SetNet(nets[net])
            t.SetLocked(True)
            board.Add(t)

    for (ox, oy), vias in ((placement.ISLAND_ORIGIN, placement.ISLAND_VIAS),
                           (placement.SCD41_ORIGIN, placement.SCD41_VIAS),
                           ((0.0, 0.0), placement.J1_GND_VIAS)):
        for net, (x, y) in vias:
            add_via(board, nets[net], ox + x, oy + y, locked=True)
    # rule areas first: the fan-out has to respect them
    for name, layers, pts, forbidden in placement.KEEPOUTS:
        rule_area(board, name, layers, pts, forbidden)
    print("GND fan-out vias:", fanout_gnd(board, nets["GND"]))

    # copper pours: GND on both outer layers, GND plane on In1, +3V3 fill on In2 (between its tracks)
    zone(board, nets["GND"], pcbnew.F_Cu, placement.POUR, "GND_TOP")
    zone(board, nets["GND"], pcbnew.B_Cu, placement.POUR, "GND_BOTTOM")
    zone(board, nets["GND"], pcbnew.In1_Cu, placement.POUR, "GND_IN1")
    zone(board, nets["+3V3"], pcbnew.In2_Cu, placement.POUR, "3V3_IN2")

    for (x0, y0), (x1, y1) in placement.SILK_LINES:
        add_line(board, pcbnew.F_SilkS, (x0, y0), (x1, y1), width=0.15)
    add_logo_placeholders(board)

    for text, x, y, opts in placement.SILK:
        opts = dict(opts)
        if "layer" in opts:
            opts["layer"] = {"F": pcbnew.F_SilkS, "B": pcbnew.B_SilkS}[opts["layer"]]
        add_text(board, text, x, y, **opts)

    tb = board.GetTitleBlock()
    tb.SetTitle(design.TITLE)
    tb.SetDate(design.DATE)
    tb.SetRevision(design.REV)
    tb.SetCompany(design.AUTHOR)

    # drill/place origin at the bottom-left corner -> positive JLCPCB CPL coordinates
    board.GetDesignSettings().SetAuxOrigin(mm(0, H))
    board.GetDesignSettings().SetGridOrigin(mm(0, H))
    out = os.path.join(project_dir, design.PROJECT + ".kicad_pcb")
    pcbnew.SaveBoard(out, board, True)  # keep gen_pro.py's project settings
    print("wrote", out, "footprints:", len(board.GetFootprints()), "nets:", board.GetNetCount())


if __name__ == "__main__":
    main(sys.argv[1])
