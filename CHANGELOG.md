# Changelog

## v3.0 "Universal": 2026-10-22, first public version (not yet manufactured)

- **Two hosts.** The board runs either as a HAT for Raspberry Pi or standalone with a user-supplied Seeed Studio XIAO ESP32-S3/C3/C6 in J7/J8.
  - Every XIAO signal has a 100 Ω series resistor.
  - Two LM66100 ideal diodes separate the 5 V sources.
  - A BAV70 enables the regulators from either 3.3 V source.
- **Long-life parts only.**
  - The BME688 was replaced by an SHT40 and an SGP41.
  - The OPT4048 colour sensor and the RV-3032 RTC with its CR1220 holder were removed.
  - The ICS-43434 microphone stays (obsolete, still stocked).
- **Connectors.** J4 (JST GH, Sensirion SEN6x/SEN5x) and J5 (Qwiic) are vertical, so the plugs clear the Pi's USB and RJ45 ports.
- **Board.**
  - 4 layers: In1 is a solid GND plane, In2 carries signals plus a 3.3 V fill.
  - 4.7 kΩ I²C pull-ups on the board.
  - Silkscreen text is at least 1 mm.
- **Software.**
  - ESPHome configs for the XIAO S3/C3/C6, plus an optional LD2410 radar package.
  - Pi test script for the I²C sensors, LED, button, buzzer and 1-Wire.
- **Licences.** Released under CERN-OHL-S-2.0 (hardware), MIT (software) and CC-BY-SA-4.0 or CERN-OHL-S-2.0 (documentation).
- **Repository.** Unused LCSC/EasyEDA parts were removed from `lib/`. The 3D models are fetched with `scripts/fetch_3d_models.py` instead of being stored in git.
- **ESPHome security.** The template now uses API encryption (also used for OTA updates) and a password for the fallback hotspot.

## v1 and v2 (unpublished)

These were Pi-only designs with a BME688 (v2 added an RTC and an OPT4048). They were never manufactured and are replaced by v3.
