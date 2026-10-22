#!/bin/zsh
# SPDX-FileCopyrightText: 2026 Emanuel Bachmann
# SPDX-License-Identifier: MIT
# Rebuild the whole Sensor HAT from scripts/design.py + scripts/placement.py.
# Usage: scripts/build.sh [--no-route]
# A failing step stops the build (pipefail); the grep filters only shorten the output.
set -e
setopt pipefail
HERE=${0:A:h}
PROJ=${HERE:h}
KICAD=~/Applications/KiCad/KiCad.app/Contents
KPY=$KICAD/Frameworks/Python.framework/Versions/3.9/bin/python3
CLI=$KICAD/MacOS/kicad-cli
JAVA=${JAVA:-/opt/homebrew/opt/openjdk/bin/java}
mkdir -p $PROJ/build            # not in git: a fresh clone has no build/ folder

python3 -I $HERE/gen_pro.py $PROJ
python3 -I $HERE/patch_lib.py $PROJ >/dev/null
python3 -I $HERE/gen_sch.py $PROJ
$CLI sch erc --severity-all -o $PROJ/build/erc.rpt $PROJ/Sensor-HAT.kicad_sch 2>/dev/null | ( grep -E "Found" || true )
$KPY -I $HERE/gen_pcb.py $PROJ 2>&1 | ( grep -E "wrote|rror" || true )
if [[ "$1" != "--no-route" ]]; then
  JAR=${FREEROUTING_JAR:?set FREEROUTING_JAR to freerouting-2.5.0.jar}
  $KPY -I $HERE/route.py $PROJ $JAR $JAVA 100 6 2>&1 | ( grep -E "attempt|best|soft|split|planes|groups|rror" || true )
  $KPY -I $HERE/repair_gnd.py $PROJ $JAR $JAVA 2>&1 | ( grep -E "isolated|tie|rip|routed|DRC|GND|rror" || true )
fi
python3 -I $HERE/cleanup.py $PROJ
$CLI pcb drc --severity-all --schematic-parity --refill-zones --save-board -o $PROJ/build/drc.rpt $PROJ/Sensor-HAT.kicad_pcb 2>/dev/null | ( grep -E "Found" || true )
