# SPDX-FileCopyrightText: 2026 Emanuel Bachmann
# SPDX-License-Identifier: MIT
"""Copy values and part fields from design.py onto the routed board (no re-placement).

For BOM-only changes after routing. Run with KiCad's Python: python3 -I sync_fields.py <project_dir>
"""
import os
import sys

import pcbnew

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import design  # noqa: E402


def main(project_dir):
    pcb = os.path.join(project_dir, design.PROJECT + ".kicad_pcb")
    board = pcbnew.LoadBoard(pcb)
    changed = []
    for part in design.PARTS:
        fp = board.FindFootprintByReference(part["ref"])
        if fp is None:
            continue
        before = (fp.GetValue(), [fp.GetFieldText(k) if fp.HasField(k) else "" for k in ("LCSC", "MPN", "Manufacturer")])
        fp.SetValue(part["value"])
        fp.SetField("Description", part.get("desc", ""))
        for key in ("LCSC", "MPN", "Manufacturer"):
            if part.get(key):
                fp.SetField(key, part[key])
        after = (fp.GetValue(), [fp.GetFieldText(k) if fp.HasField(k) else "" for k in ("LCSC", "MPN", "Manufacturer")])
        if before != after:
            changed.append(part["ref"])
    pcbnew.SaveBoard(pcb, board, True)
    print("fields updated:", changed or "none")


if __name__ == "__main__":
    main(sys.argv[1])
