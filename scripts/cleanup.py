# SPDX-FileCopyrightText: 2026 Emanuel Bachmann
# SPDX-License-Identifier: MIT
"""Remove vias the autorouter left connected on one layer only (DRC 'via_dangling').

Works on the board file text: deleting items through the SWIG API corrupts its
type table. Zones are refilled afterwards by `kicad-cli pcb drc --refill-zones --save-board`.
Usage: python3 -I cleanup.py <project_dir>
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import design  # noqa: E402
from sexpr import dump, find, parse  # noqa: E402

CLI = os.path.expanduser("~/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli")


def dangling_vias(pcb, report):
    subprocess.run([CLI, "pcb", "drc", "--format", "json", "--severity-all", "-o", report, pcb],
                   capture_output=True)
    d = json.load(open(report, encoding="utf-8"))
    out, stubs = [], set()
    for v in d.get("violations", []):
        if v.get("type") == "via_dangling":
            for item in v.get("items", []):
                pos = item.get("pos", {})
                out.append((round(pos["x"], 3), round(pos["y"], 3)))
        elif v.get("type") == "track_dangling":
            # dead-end stub, typically left behind by a removed one-layer via
            stubs.update(item["uuid"] for item in v.get("items", []) if item.get("uuid"))
    return out, stubs


def main(project_dir):
    pcb = os.path.join(project_dir, design.PROJECT + ".kicad_pcb")
    report = os.path.join(project_dir, "build", "cleanup.json")
    removed = 0
    removed_stubs = 0
    removed_segments = []
    for n in range(5):
        vias, stubs = dangling_vias(pcb, report)
        targets = set(vias)
        if not targets and not stubs and n > 0:
            break
        tree = parse(open(pcb, encoding="utf-8").read())
        keep = []
        for x in tree:
            if isinstance(x, list) and x and x[0] == "segment":
                uid, locked = find(x, "uuid"), find(x, "locked")
                if uid and str(uid[1]) in stubs and not (locked and locked[1] == "yes"):
                    removed_stubs += 1
                    continue
                st, en = find(x, "start"), find(x, "end")
                if abs(float(st[1]) - float(en[1])) < 0.001 and abs(float(st[2]) - float(en[2])) < 0.001:
                    removed_segments.append(1)
                    continue
            if isinstance(x, list) and x and x[0] == "via":
                at = find(x, "at")
                if (round(float(at[1]), 3), round(float(at[2]), 3)) in targets:
                    removed += 1
                    continue
            keep.append(x)
        tree[:] = keep
        with open(pcb, "w", encoding="utf-8") as f:
            f.write(dump(tree) + "\n")
        subprocess.run([CLI, "pcb", "drc", "--refill-zones", "--save-board", "-o", report, pcb],
                       capture_output=True)
    print("dangling vias removed:", removed, "| dead-end stubs removed:", removed_stubs,
          "| zero-length segments removed:", len(removed_segments))


if __name__ == "__main__":
    main(sys.argv[1])
