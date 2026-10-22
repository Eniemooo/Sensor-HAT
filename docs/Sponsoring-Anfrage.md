# Sponsoring-Anfrage für den Prototyp (Vorlage)

Mehrere Leiterplattenhersteller sponsern Open-Source-Projekte mit kostenlosen oder vergünstigten Prototypen. Im Gegenzug erwarten sie eine Erwähnung oder einen kurzen Bericht.

| Anbieter | Wo anfragen | Hinweis |
|---|---|---|
| **PCBWay** | pcbway.com/project/sponsorpublish oder sponsor@pcbway.com | Non-Profit-Sponsoring. Die 10-%-Beteiligung bei geteilten Projekten **ablehnen**, sonst wäre es kommerziell. |
| **Elecrow** | elecrow.com/activity/sponsorship | Die Frage nach dem Partner-Verkaufsprogramm mit **Nein** beantworten. |
| NextPCB Accelerator | nextpcb.com (Kampagnen) | Nur wenn die laufende Kampagne einen Chip verlangt, der auf der Platine ist. |

**Vorher prüfen**:
- Kann der Anbieter SCD41, SGP41, SHT40 und ICS-43434 beschaffen?
- Hält er beim Löten 245 °C Spitze ein?
- Wäscht er die Platine nicht (Sensoren)?

Ohne Zusage nach etwa 3 Wochen gibt es den 5er-Pilot bei JLCPCB (siehe `docs/Sammelbestellung.md`).

---

## Text (Englisch, zum Kopieren)

**Subject: Sponsorship request – open-source indoor air-quality board (HAT for Raspberry Pi / Seeed XIAO)**

Hello [PCBWay / Elecrow] team,

I'm a hobbyist from Germany. I designed an open-source indoor-environment sensor board and would like to ask for sponsorship of the first prototype run (PCB + assembly, 2–5 boards).

**Project**: Sensor HAT v3 "Universal". A 65 × 56 mm 4-layer board (signal / GND / signal + 3V3 / signal, 1.6 mm, ENIG) that works either as a HAT for Raspberry Pi (HAT+ ID EEPROM) or standalone with a plug-in Seeed XIAO ESP32-S3/C3/C6 running ESPHome / Home Assistant.

**Sensors**: Sensirion SCD41 (photoacoustic CO₂), SHT40 (T/RH on a milled, thermally isolated island), SGP41 (VOC/NOx index), Vishay VEML7700 (lux), TDK ICS-43434 (I²S microphone, sound level). Plus an RGB status LED, button and buzzer, and ports for Sensirion SEN6x/SEN5x particulate sensors, mmWave radar, 1-Wire and Qwiic.

**Design files**: KiCad 10 project, Gerber/BOM/CPL, ESPHome YAML and Python, all public at https://github.com/Eniemooo/Sensor-HAT under CERN-OHL-S-2.0 (hardware), MIT (software) and CC-BY-SA-4.0 or CERN-OHL-S-2.0 (docs). Some symbols and footprints come from the LCSC/EasyEDA library, see NOTICE.md.

**Assembly notes**: top-side SMT only, single reflow, peak ≤ 245 °C (SCD41/SGP41 limit), no washing, keep the ICS-43434 bottom acoustic port clear. LGA/DFN parts need X-ray inspection.

**What I offer in return**:
- a build log with photos and measurement results (CO₂ against a reference, thermal offset, sound level)
- publication on [Hackaday.io / GitHub / Home Assistant forum]
- your logo and link in the README and on the board silkscreen if you like

The project is non-commercial: one at-cost community group order is planned afterwards. I do not intend to sell the design.

Thank you for considering it!

Best regards,
[Name]
[E-mail]
