# Interessenten-Aufruf (zum Kopieren ins Forum)

Platzhalter in [eckigen Klammern] vor dem Posten ersetzen. Fotos und das 3D-Bild aus `docs/` anhängen.

---

## Deutsch

**[Interesse?] Open-Hardware-Raumsensor: echtes CO₂ + VOC/NOx + Temperatur/Feuchte + Licht + Lautstärke – als HAT für den Raspberry Pi oder mit Seeed XIAO (ESPHome)**

Hallo zusammen,

ich habe eine Sensorplatine entworfen und suche Leute, die mitbestellen möchten. Bei einer gemeinsamen Bestellung wird sie deutlich günstiger. Das Projekt ist offen: das KiCad-Projekt unter CERN-OHL-S-2.0, ESPHome-Konfiguration und Python unter MIT. Einige Symbole und Footprints stammen aus der LCSC/EasyEDA-Bibliothek, für die keine eigene Lizenz angegeben ist (siehe NOTICE.md): https://github.com/Eniemooo/Sensor-HAT

**Was drauf ist**
- **Sensirion SCD41**: echte CO₂-Messung (photoakustisch, kein geschätzter eCO₂-Wert)
- **Sensirion SHT40**: Temperatur und Luftfeuchte, auf einer gefrästen Insel vom Rest der Platine thermisch entkoppelt
- **Sensirion SGP41**: VOC- und NOx-Index (offener Algorithmus)
- **Vishay VEML7700**: Helligkeit in Lux
- **I²S-Mikrofon**: Lautstärke (ungefähr dB, unbewertet; die mitgelieferte ESPHome-Konfiguration wertet nur den Pegel aus und sendet kein Audio)
- RGB-Status-LED (z. B. als CO₂-Ampel), Taster, Summer
- Anschlüsse:
  - Sensirion-Feinstaubsensor SEN6x/SEN5x (JST GH)
  - mmWave-Präsenzradar (z. B. HLK-LD2420)
  - DS18B20
  - Qwiic
  - freie GPIOs

**Zwei Betriebsarten, eine Platine**
1. **HAT für den Raspberry Pi** (Pi 2/3/4/5, HAT+-EEPROM), Auswertung mit Python.
2. **Eigenständig mit Seeed XIAO ESP32-S3/C3/C6** (steckbar, kaufst du selbst für ca. 8–10 €). Läuft mit ESPHome und erscheint direkt in Home Assistant. Strom über USB-C.

**Was es kosten würde** (geschätzt, pro Platine fertig bestückt inkl. XIAO-Buchsen und Steckleisten, inkl. MwSt., zzgl. Versand innerhalb DE; die 40-polige Pi-Buchse lötest du selbst, ca. 1 €):
- bei 20 Teilnehmern ca. 55 €
- bei 50 ca. 45 €
- bei 100 ca. 40 €

Darin ist eine Ersatzplatine schon eingerechnet. Bei der Vorkasse kommen 10 % Puffer für Wechselkurs und Zoll dazu, der Rest geht nach der Abrechnung zurück.

Zum Vergleich: Allein ein SCD41-Breakout kostet im Handel ca. 50 €.

**Wie es abläuft**: einmalige private Sammelbestellung zum Selbstkostenpreis, keine Marge, Abrechnung wird offengelegt. Erst ein Prototyp, dann eine verbindliche Runde mit Vorkasse ab 20 Teilnehmern, sonst Geld zurück. Die Platinen sind ein Hobbyprojekt ohne Gewährleistung.

**Bitte kurz antworten (unverbindlich):**
1. Interesse ja/nein, wie viele Platinen?
2. Nutzung mit Pi oder mit XIAO/ESPHome?
3. Würdest du lieber eine günstigere Version ohne CO₂-Sensor (ca. 20 € billiger) nehmen?
4. Fehlt dir etwas Wichtiges?

Danke! [Name]

*Raspberry Pi ist eine Marke der Raspberry Pi Ltd. Das Projekt steht in keiner Verbindung zu Raspberry Pi Ltd oder Seeed Studio.*

---

## English

**[Interest check] Open-hardware room sensor: true CO₂ + VOC/NOx + T/RH + light + sound level – as a HAT for Raspberry Pi or with a Seeed XIAO (ESPHome)**

Hi all,

I designed a sensor board and I'm looking for people who'd like to join a group order, which makes it much cheaper. Open hardware: the KiCad project under CERN-OHL-S-2.0, ESPHome config and Python under MIT. Some symbols and footprints come from the LCSC/EasyEDA library, which has no licence of its own (see NOTICE.md): https://github.com/Eniemooo/Sensor-HAT

**Sensors**
- Sensirion SCD41: real photoacoustic CO₂, no eCO₂ estimate
- SHT40: T/RH on a milled island, thermally isolated from the rest of the board
- SGP41: VOC and NOx index
- VEML7700: lux
- I²S microphone: sound level only (the supplied ESPHome config sends no audio)
- RGB status LED (CO₂ traffic light), button, buzzer

**Ports**: Sensirion SEN6x/SEN5x PM sensor (JST GH), mmWave radar (e.g. HLK-LD2420), DS18B20, Qwiic, spare GPIOs.

**Two modes**
1. HAT for Raspberry Pi (HAT+ EEPROM, Python).
2. Standalone with a plug-in Seeed XIAO ESP32-S3/C3/C6 that you buy yourself (about 8–10 €). ESPHome, appears in Home Assistant, powered over USB-C.

**Estimated price** per fully assembled board incl. XIAO sockets and pin headers, incl. 19 % VAT and one spare board (shipping within Germany extra; you solder the 40-pin Pi socket yourself; prepayment adds a 10 % buffer that is refunded after the final invoice):
- about 55 € with 20 people
- about 45 € with 50
- about 40 € with 100

**How it works**: one private, at-cost group order with no margin and published invoice. First a prototype, then a binding round with prepayment once 20 people have paid, otherwise full refund. Hobby project, no warranty.

**Please reply (non-binding):** interested? how many? Pi or XIAO/ESPHome? would you prefer a cheaper version without CO₂? anything missing?

Thanks! [name]

*Raspberry Pi is a trademark of Raspberry Pi Ltd. This project is not affiliated with Raspberry Pi Ltd or Seeed Studio.*
