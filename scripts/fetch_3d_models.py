# SPDX-FileCopyrightText: 2026 Emanuel Bachmann
# SPDX-License-Identifier: MIT
"""Download the LCSC/EasyEDA 3D models that the project footprints reference.

The models are not part of the repository (third-party files without a clear licence,
about 40 MB). KiCad only needs them for the 3D viewer, the renders and the STEP export;
Gerber, BOM and CPL do not depend on them.

    pip install easyeda2kicad
    python3 -I fetch_3d_models.py <project_dir> [path/to/easyeda2kicad]

Writes lib/SensorHAT.3dshapes/<model>.wrl and .step for every part in design.py that uses
a SensorHAT footprint. Existing files are overwritten. Exits with 1 if a model is missing.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import design  # noqa: E402

MODEL_DIR = "${KIPRJMOD}/lib/SensorHAT.3dshapes/"


def main(project_dir, tool="easyeda2kicad"):
    pretty = os.path.join(project_dir, "lib", "SensorHAT.pretty")
    dest = os.path.join(project_dir, "lib", "SensorHAT.3dshapes")
    needed, lcsc = set(), set()
    for p in design.PARTS:
        fp = p.get("fp", "")
        if not fp.startswith("SensorHAT:"):
            continue
        text = open(os.path.join(pretty, fp.split(":")[1] + ".kicad_mod"), encoding="utf-8").read()
        m = re.search(r'\(model "([^"]+)"', text)
        if m and m.group(1).startswith(MODEL_DIR):
            needed.add(os.path.splitext(m.group(1)[len(MODEL_DIR):])[0])
            lcsc.add(p["LCSC"])
    os.makedirs(dest, exist_ok=True)
    missing = 0
    with tempfile.TemporaryDirectory() as tmp:
        for part in sorted(lcsc):
            try:
                subprocess.run([tool, "--3d", "--overwrite", "--lcsc_id", part, "--output", os.path.join(tmp, "lib")],
                               check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except FileNotFoundError:
                sys.exit(f"{tool} not found: pip install easyeda2kicad, or pass its path as second argument")
        shapes = os.path.join(tmp, "lib.3dshapes")
        for stem in sorted(needed):
            got = [ext for ext in (".wrl", ".step") if os.path.exists(os.path.join(shapes, stem + ext))]
            for ext in got:
                shutil.copy(os.path.join(shapes, stem + ext), dest)
            missing += len(got) != 2
            print(("ok      " if len(got) == 2 else "MISSING ") + stem + " " + " ".join(got))
    if missing:
        sys.exit(f"{missing} model(s) incomplete (network or LCSC change?)")


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        sys.exit(__doc__)
    main(*sys.argv[1:])
