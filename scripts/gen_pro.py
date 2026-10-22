# SPDX-FileCopyrightText: 2026 Emanuel Bachmann
# SPDX-License-Identifier: MIT
"""Write Sensor-HAT.kicad_pro from KiCad's RaspberryPi-HAT template with JLCPCB rules.

Usage: python3 -I gen_pro.py <project_dir>
"""
import json
import os
import sys
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import design  # noqa: E402
from kicadlib import KICAD_SHARE  # noqa: E402

TEMPLATE = os.path.join(KICAD_SHARE, "template", "RaspberryPi-HAT", "RaspberryPi-HAT.kicad_pro")

POWER_NETS = ["GND", "+5V", "+5V_PI", "+5V_XIAO", "+5V_FUSED", "+5V_SW", "+3V3", "+3V3_CO2", "+3V3_PI", "+3V3_PM", "PM_VCC",
              "UART_VCC"]


def main(project_dir):
    with open(TEMPLATE, encoding="utf-8") as f:
        pro = json.load(f)
    pro["meta"]["filename"] = design.PROJECT + ".kicad_pro"

    ds = pro["board"]["design_settings"]
    # Conservative JLCPCB 2-layer standard process values
    ds["rules"].update({
        "min_clearance": 0.15,
        "min_track_width": 0.12,   # JLC 2-layer: 0.10 mm; the autorouter necks to 0.125 at a few pads
        "min_connection": 0.12,
        "min_via_diameter": 0.6,
        "min_via_annular_width": 0.15,
        "min_through_hole_diameter": 0.3,
        "min_hole_clearance": 0.25,
        "min_hole_to_hole": 0.5,
        "min_copper_edge_clearance": 0.3,
        "min_silk_clearance": 0.0,
        "min_text_height": 1.0,
        "min_text_thickness": 0.15,
        "min_resolved_spokes": 1,
    })
    ds["track_widths"] = [0.0, 0.2, 0.25, 0.4, 0.5, 0.8]
    ds["via_dimensions"] = [{"diameter": 0.0, "drill": 0.0}, {"diameter": 0.6, "drill": 0.3},
                            {"diameter": 0.8, "drill": 0.4}]
    # silkscreen overlapping pads is clipped by JLC anyway; keep it a warning
    for rule in ("silk_over_copper", "silk_overlap", "silk_edge_clearance", "lib_footprint_mismatch"):
        ds["rule_severities"][rule] = "warning"
    ds["rule_severities"]["lib_footprint_issues"] = "ignore"

    default = dict(pro["net_settings"]["classes"][0])
    default.update({"clearance": 0.2, "track_width": 0.25, "via_diameter": 0.6, "via_drill": 0.3})
    power = dict(default)
    power.update({"name": "Power", "track_width": 0.4, "via_diameter": 0.6, "via_drill": 0.3,
                  "priority": 0, "schematic_color": "rgba(194, 0, 0, 1.000)"})
    pro["net_settings"]["classes"] = [default, power]
    pro["net_settings"]["netclass_patterns"] = [{"netclass": "Power", "pattern": "/" + n} for n in POWER_NETS]

    pro["sheets"] = [[str(uuid.uuid5(design.NAMESPACE, "root-sheet")), "Root"]]
    pro["text_variables"] = {}
    out = os.path.join(project_dir, design.PROJECT + ".kicad_pro")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(pro, f, indent=2)
    print("wrote", out)


if __name__ == "__main__":
    main(sys.argv[1])
