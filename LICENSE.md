# Licences

Copyright 2026 Emanuel Bachmann. Different parts of this project use different licences:

| What | Licence | Full text |
|---|---|---|
| **Hardware**: KiCad project (`Sensor-HAT.kicad_*`, `fp-lib-table`, `sym-lib-table`), the design data `scripts/design.py` and `scripts/placement.py`, production files (`production/`), schematic and assembly PDFs and renders (`docs/*.pdf`, `docs/*.png`) | CERN Open Hardware Licence v2, Strongly Reciprocal (**CERN-OHL-S-2.0**) | [LICENSES/CERN-OHL-S-2.0.txt](LICENSES/CERN-OHL-S-2.0.txt) |
| **Software and tools**: everything in `software/` (ESPHome, Python, Pi configuration) and the generator scripts in `scripts/` except the two design files above | **MIT** | [LICENSES/MIT.txt](LICENSES/MIT.txt) |
| **Documentation**: `README.md`, `README.de.md`, `CHANGELOG.md`, `NOTICE.md`, `docs/*.md` | Creative Commons Attribution-ShareAlike 4.0 (**CC-BY-SA-4.0**) or, at your choice, **CERN-OHL-S-2.0** | [LICENSES/CC-BY-SA-4.0.txt](LICENSES/CC-BY-SA-4.0.txt), [LICENSES/CERN-OHL-S-2.0.txt](LICENSES/CERN-OHL-S-2.0.txt) |
| **Third-party library parts** in `lib/`, also embedded in the schematic and board, and contained in the production files, PDFs and renders made from them | no licence of their own, see [NOTICE.md](NOTICE.md) | [LICENSES/LicenseRef-LCSC-EasyEDA-Library.txt](LICENSES/LicenseRef-LCSC-EasyEDA-Library.txt) |

Every file states its licence, either in an SPDX header or in [REUSE.toml](REUSE.toml). The project follows the [REUSE](https://reuse.software) convention, so `reuse lint` checks it.

## What CERN-OHL-S means in practice

- You may use, study, change, manufacture and sell the board, also commercially.
- If you pass on the design, a changed design or boards made from it, you must:
  - keep the notices
  - pass on the complete design source, or say where to get it, under CERN-OHL-S as well (this includes your changes)
- Changed versions need a note saying what you changed and when.

Source Location (CERN-OHL-S section 1.9): <https://github.com/Eniemooo/Sensor-HAT>

## No warranty

The design has not been tested in hardware yet. It is provided "as is", without any warranty. See section 6 of the CERN-OHL-S, the MIT licence and section 5 of CC-BY-SA-4.0.
