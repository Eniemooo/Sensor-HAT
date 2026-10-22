# Third-party material and trademarks

## KiCad libraries and template

The schematic and board contain symbols and footprints from the official KiCad libraries. The board and project were also generated from KiCad's `RaspberryPi-HAT` template. The KiCad libraries are licensed under CC-BY-SA-4.0 with an exception for designs that use them (<https://www.kicad.org/libraries/license/>). That exception covers this design and the files generated from it.

The KiCad libraries themselves are not redistributed here, with one exception:

- `lib/SensorHAT.pretty/SHT4x_DFN-4_1.5x1.5mm_P0.8mm_NoCentralPad.kicad_mod` is a copy of the KiCad footprint `Sensor_Humidity:Sensirion_DFN-4_1.5x1.5mm_P0.8mm_SHT4x_NoCentralPad` by the KiCad Library Team.
  - Original: <https://gitlab.com/kicad/libraries/kicad-footprints> (`Sensor_Humidity.pretty`, KiCad 10.0).
- On 2026-10-22 it was renamed and its keepout zone was removed. With the keepout, Freerouting treated the island traces as violations and left whole nets unrouted.
- This file stays under CC-BY-SA-4.0.

## LCSC / EasyEDA component data

All other symbols (`lib/SensorHAT.kicad_sym`) and footprints (`lib/SensorHAT.pretty/`) were converted with [easyeda2kicad](https://github.com/uPesy/easyeda2kicad.py) from the LCSC / EasyEDA component library. Each part carries its LCSC number. The schematic and board embed copies of these parts.

- **No specific licence.** No specific licence is stated for this library data. EasyEDA's general Terms of Service (<https://easyeda.com/legal>) restrict site content to personal, non-commercial use. The data is included in good faith, without an explicit permission to redistribute it, only so that the design opens and can be manufactured. See [LICENSES/LicenseRef-LCSC-EasyEDA-Library.txt](LICENSES/LicenseRef-LCSC-EasyEDA-Library.txt). If you hold rights in it and object, please open an issue.
- **Project changes.** The changes this project made to these parts are licensed under CERN-OHL-S-2.0:
  - pad and paste corrections written by `scripts/patch_lib.py` (the script itself is MIT)
  - renamed pads
  - added courtyards
  - copied symbols
- **3D models.** The 3D models are not included. They also come from LCSC/EasyEDA. KiCad needs them only for the 3D view, the renders and the STEP export. The renders in `docs/*.png` show these models. To fetch them:

  ```bash
  pip install easyeda2kicad
  python3 -I scripts/fetch_3d_models.py .
  ```

## Tools

The board was generated and routed with KiCad 10 (GPL-3.0-or-later) and [Freerouting](https://github.com/freerouting/freerouting) 2.5 (GPL-3.0). Neither is included. Their output, this design, is not covered by their licences.

## Trademarks

Raspberry Pi is a trademark of Raspberry Pi Ltd. All other product and company names are trademarks of their respective owners. They are used here only to describe compatibility. This project is not affiliated with or endorsed by any of them. The names include:

- Seeed Studio XIAO (Seeed Technology)
- Sensirion
- Vishay
- TDK InvenSense
- Qwiic (SparkFun)
- STEMMA QT (Adafruit)
- JST
- JLCPCB, LCSC and EasyEDA
- Home Assistant
- ESPHome
