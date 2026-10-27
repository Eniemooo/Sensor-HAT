# Sensor HAT v3 „Universal“

*English: [README.md](README.md)*

Offene Raumsensor-Platine (KiCad 10, 65 × 56 mm, 4 Lagen) für **zwei Betriebsarten**:

1. **HAT für den Raspberry Pi** 2, 3, 4 und 5, mit HAT+-ID-EEPROM, Auswertung mit Python.
2. **Eigenständig mit einem Seeed XIAO ESP32-S3, -C3 oder -C6** im Steckplatz J7/J8, Strom über USB-C, Firmware ESPHome. Der Sensor erscheint direkt in Home Assistant.

**Nie beides gleichzeitig.** Wenn die Platine auf einem Pi steckt, gehört kein XIAO in den Steckplatz.

**Sponsor:** Die Leiterplatten der Prototypen sponsert [AISLER](https://aisler.net), Leiterplattenfertigung in Deutschland. Danke! Das Rechteck auf dem Bestückungsdruck der Unterseite ist AISLERs Logo-Platzhalter, den AISLER bei der Fertigung durch sein Logo ersetzt.

| Funktion | Bauteil | I²C / Pi-GPIO / XIAO-Pin |
|---|---|---|
| CO₂ (photoakustisch, echt) | Sensirion SCD41 (U1), eigener 3,3-V-Regler | 0x62 |
| Temperatur, Luftfeuchte | Sensirion SHT40 (U2) auf gefräster Insel | 0x44 |
| VOC- und NOx-Index | Sensirion SGP41 (U13) | 0x59 |
| Helligkeit (Lux) | Vishay VEML7700-TT (U7) | 0x10 |
| Lautstärke | TDK ICS-43434 I²S-Mikrofon (U3) | Pi GPIO18/19/20, XIAO D1/D0/D2 |
| RGB-Status-LED (z. B. CO₂-Ampel) | WS2812B-2020 (D1) mit 5-V-Pegelwandler | Pi GPIO10, XIAO D10 |
| Taster | SW1 | Pi GPIO27, XIAO D4 |
| Summer (passiv, 4 kHz) | MLT-5020 (LS1) | Pi GPIO13, XIAO D3 |
| Feinstaub-Anschluss (Sensirion SEN6x/SEN5x) | J4, JST GH 6-polig senkrecht, eigener Regler U9 | 0x6B / 0x69 |
| Radar / UART (z. B. HLK-LD2420, LD2410S) | J3 | Pi GPIO14/15 (+GPIO17 OUT), XIAO D6/D7 |
| 1-Wire (z. B. DS18B20) | J2 | Pi GPIO4, XIAO D5 (JP6) |
| Qwiic / STEMMA QT | J5, JST SH 4-polig senkrecht | I²C 3,3 V |
| Freie GPIOs (nur Pi) | J6, 2×5 Lötpunkte (nicht bestückt) | GPIO5, 12, 22–26 |
| HAT-Kennung | onsemi CAT24C32 (U4) | Pi ID_SD/ID_SC, 0x50 |

## Ordner

| Pfad | Inhalt |
|---|---|
| `Sensor-HAT.kicad_pro/.kicad_sch/.kicad_pcb` | KiCad-Projekt (mit KiCad 10 öffnen) |
| `production/` | **Fertigungsdaten für JLCPCB**: Gerber-ZIP, BOM, CPL |
| `docs/` | Schaltplan-PDF, Bestückungsplan, 3D-Bilder; **Sammelbestellung, Interessenten-Aufruf, Sponsoring-Anfrage** |
| `software/` | Pi: `config.txt`-Zeilen, EEPROM-Inhalt, `sensor_test.py`. XIAO: `esphome/` |
| `lib/` | Symbole und Footprints der LCSC-Bauteile. Die 3D-Modelle sind nicht im Repository, `scripts/fetch_3d_models.py` lädt sie |
| `scripts/` | Generator (`design.py`, `placement.py`, `build.sh` …), `cost.py` (Kosten je Stückzahl), `import_lcsc.py`, `fetch_3d_models.py` |
| `LICENSES/`, `LICENSE.md`, `NOTICE.md` | Lizenztexte, welche Lizenz wofür gilt, fremde Bauteildaten und Marken |

`build/` (Routing-Zwischenstände und Berichte) ist nicht im Repository, `scripts/build.sh` und `scripts/export.py` legen es neu an. Die STEP-Datei (19 MB) enthält die LCSC/EasyEDA-3D-Modelle und wird deshalb nicht veröffentlicht. Lokal erzeugen: erst `fetch_3d_models.py`, dann `export.py`.

## Was sich gegenüber v2 geändert hat

- **Nur noch Bauteile, die aktiv hergestellt werden und breit verfügbar sind.**
  - BME688 → **SHT40 + SGP41**. Offener Algorithmus und volle ESPHome-Unterstützung; dafür kein Luftdruck mehr.
  - Farbsensor OPT4048 entfernt: kaum Lager und keine Treiber.
  - Echtzeituhr mit Knopfzelle entfernt: Pi und ESP holen die Zeit per NTP, und der Platz wird für den XIAO gebraucht.
  - Einzige Ausnahme ist das Mikrofon ICS-43434. Es ist abgekündigt, aber bei DigiKey liegen noch rund 79.000 Stück. Für eine Sammelbestellung reicht das, vor der Bestellung reservieren.
- **XIAO-Steckplatz** mit 100-Ω-Schutzwiderständen in jeder Signalleitung. Die Pinbelegung ist für S3, C3 und C6 boot-sicher geprüft.
- **Zwei Stromquellen sauber getrennt**: zwei „ideale Dioden“ (TI LM66100). Es fließt kein Strom vom Pi in den USB-Anschluss oder umgekehrt. Die Regler werden über eine Doppeldiode (BAV70) eingeschaltet, sobald Pi-3V3 **oder** XIAO-3V3 anliegt. Damit schaltet die Platine ab, wenn der Pi seine 3,3 V abschaltet (HAT+-Standby).
- **I²C-Pull-ups auf der Platine** (4,7 kΩ), damit der XIAO-Betrieb funktioniert. Am Pi liegen sie parallel zu dessen 1,8 kΩ, das ist unkritisch.
- **4 Lagen statt 2**: Lage 2 (In1) ist eine geschlossene Massefläche (ausgespart sind nur die Sensor-Insel, die Befestigungslöcher und das Mikrofonloch). Lage 3 (In2) trägt Leiterbahnen, und ihre freie Fläche ist mit 3,3 V gefüllt. Erst damit ließ sich die dichtere Platine sauber routen. Außerdem verbessert die geschlossene Massefläche Störfestigkeit und Störaussendung (wichtig für eine spätere CE-Prüfung). Mehrkosten: grob 10–15 € für 5 Prototypen, unter 2 € pro Platine bei einer Sammelbestellung.
- Weniger Bauteilsorten (33 SMD-Sorten), deshalb niedrigere Bestückungsgebühren.

## Die zwei Betriebsarten

### Raspberry-Pi-Modus
- XIAO-Steckplatz leer lassen.
- Die Platine bekommt 5 V vom Pi und erzeugt ihre 3,3 V mit eigenen Reglern. Diese laufen, solange am 3V3-Pin des Pi Spannung anliegt.
- **Nach dem Herunterfahren bleibt die Platine standardmäßig an**: Pi 2/3 schalten 3V3 nie ab, Pi 4/5 im Standard „WARM-STANDBY“ auch nicht. Ganz abschalten nur am Pi 4/5 mit `sudo rpi-eeprom-config -e` und `POWER_OFF_ON_HALT=1`, `WAKE_ON_GPIO=0`.
- Software: siehe [Inbetriebnahme am Pi](#inbetriebnahme-am-raspberry-pi).

### XIAO-Modus (ESPHome / Home Assistant)
- XIAO ESP32-S3 (empfohlen), -C3 oder -C6 mit **USB-C nach außen** in J7/J8 stecken. Die Beschriftung „XIAO USB-C“ steht am linken Rand.
- Versorgung über das USB-C-Kabel des XIAO: **mindestens 5 V / 1,5 A** mit Feinstaubsensor und Radar, sonst mindestens 1 A. Ein PC-USB-Port reicht nicht.
- **Keinen Akku an den XIAO anschließen.** Ohne USB läuft der XIAO am Akku weiter und speist über seine Ausgänge die dann stromlosen Sensoren zurück. Das kann Mikrofon und Sensoren schädigen.
- ESP32-S3 und -C3 haben keine eingebaute Antenne: die beiliegende U.FL-Antenne anschließen und vom Board weg führen. Der C6 hat zwar eine Chip-Antenne, sie sitzt aber 11 mm über der Massefläche. Für guten Empfang auch beim C6 eine U.FL-Antenne verwenden (in ESPHome `antenna_select` auf HIGH).
- Software: siehe [Inbetriebnahme mit XIAO](#inbetriebnahme-mit-xiao-esphome).

### Pinbelegung

| Funktion | Pi (BCM) | XIAO | S3 / C3 / C6 GPIO |
|---|---|---|---|
| I²S LRCLK | 19 | D0 | 1 / 2 / 0 |
| I²S BCLK | 18 | D1 | 2 / 3 / 1 |
| I²S Daten (Mikro) | 20 | D2 | 3 / 4 / 2 |
| Summer | 13 | D3 | 4 / 5 / 21 |
| Taster | 27 | D4 | 5 / 6 / 22 |
| 1-Wire (JP6 1-2) bzw. Radar OUT (JP6 2-3) | 4 bzw. 17 | D5 | 6 / 7 / 23 |
| UART TX → Radar RX | 14 | D6 | 43 / 21 / 16 |
| UART RX ← Radar TX | 15 | D7 | 44 / 20 / 17 |
| I²C SDA | 2 | D8 | 7 / 8 / 19 |
| I²C SCL | 3 | D9 | 8 / 9 / 20 |
| RGB-LED | 10 | D10 | 9 / 10 / 18 |

ESPHome warnt beim C3 (GPIO2/8/9) und beim S3 (GPIO3) vor „Strapping-Pins“. Auf dieser Platine sind diese Pins hochgezogen oder werden nicht ausgewertet. Die Warnungen sind also erwartet und unkritisch.

## Bei JLCPCB bestellen

Im Ordner `production/` liegen zwei Varianten:

| Variante | BOM | CPL | Was JLCPCB lötet |
|---|---|---|---|
| **Komplett** | `Sensor-HAT-BOM-jlcpcb-komplett.csv` | `Sensor-HAT-CPL-jlcpcb-komplett.csv` | alles außer J1, also auch J2, J3 und die XIAO-Buchsen J7/J8 (von Hand, +1 Tag) |
| **Nur SMD** | `Sensor-HAT-BOM-jlcpcb.csv` | `Sensor-HAT-CPL-jlcpcb.csv` | alles außer J1, J2, J3, J7, J8 (Liste in `Sensor-HAT-BOM-handloeten.csv`) |

**J1 (40-polige Pi-Buchse) lötest du immer selbst.** Sie sitzt als einziges Teil auf der Unterseite, und JLCPCB würde sonst beidseitige Bestückung berechnen. J6 ist in keiner Variante bestückt.

1. **Gerber** hochladen: `production/Sensor-HAT-gerber-jlcpcb.zip`, **4 Lagen**, 1,6 mm, Standard-Lagenaufbau.
   - **ENIG** empfohlen: ebene Pads für die LGA/DFN-Sensoren.
2. **PCB Assembly**:
   - **Standard** (Economic geht nicht: SCD41, SGP41 und Mikrofon sind „Standard only“, max. 245 °C)
   - Top Side, Tooling holes „Added by JLCPCB“. Standard braucht mindestens 70 × 70 mm, JLCPCB setzt deshalb Randstreifen an. Die Platine ist 65 × 56 mm groß, also braucht es Streifen links, rechts und oben (zusammen etwa 75 × 70 mm), nie am unteren Rand mit der Sensor-Insel. Das in die Bemerkung schreiben (siehe unten) und von JLCPCB bestätigen lassen.
   - Board Cleaning **Nein**
3. **BOM und CPL** hochladen, alle Zeilen bestätigen.
4. **Platzierungsvorschau** prüfen (Pin 1 und Drehung):
   - U1 SCD41, U2 SHT40, U13 SGP41, U3 Mikrofon, U7 VEML7700
   - U14/U15 LM66100, D3 BAV70, U12, D1 LED, D2
   - J4/J5 senkrecht
   - Optional „Confirm Parts Placement“ (0,45 $).
5. **Bemerkung**:
   > Standard PCBA, top-side SMT, single reflow, peak max 245 °C. Edge rails on the left and right edges (x = 0 and x = 65) and on the top edge, about 75 x 70 mm in total; no rail and no V-cut along the bottom edge (milled sensor island). Do NOT wash the board (SCD41, SHT40, SGP41, ICS-43434) and do not cover the SGP41/SHT40 with tape. Keep the ICS-43434 acoustic hole (bottom port) free of flux. J1 is not assembled (hand-soldered by the customer). J7/J8 are XIAO sockets on top. J6 not populated.
6. **Versand**: DHL Express DDP, dann ist die Mehrwertsteuer schon bezahlt.

### Kosten

Mindestens 5 Leiterplatten, davon mindestens 2 bestückt. Die festen Gebühren pro Bestellung (Einrichtung, Schablone, 1,53 $ je Bauteilsorte, Röntgen der LGA-Sensoren, Versand) machen kleine Mengen teuer.

`python3 -I scripts/cost.py 2 5 20 50 100` rechnet das mit aktuellen JLCPCB-Preisen aus. Stand 22.10.2026, geliefert inkl. 19 % MwSt., geschätzt:

| bestückte Platinen | pro Platine (Stiftleisten selbst gelötet) | gesamt |
|---|---|---|
| 2 | ca. 125 € | ca. 250 € |
| 5 | ca. 77 € | ca. 385 € |
| 20 | ca. 50 € | ca. 1.010 € |
| 50 | ca. 42 € | ca. 2.110 € |
| 100 | ca. 37 € | ca. 3.680 € |

Deshalb: **Sammelbestellung**. Ablauf, Regeln und rechtliche Leitplanken stehen in [docs/Sammelbestellung.md](docs/Sammelbestellung.md). Ein Text zum Posten steht in [docs/Interessenten-Aufruf.md](docs/Interessenten-Aufruf.md), eine Vorlage für ein kostenloses Prototyp-Sponsoring in [docs/Sponsoring-Anfrage.md](docs/Sponsoring-Anfrage.md).

## Montage

- **Pi-Modus**: Buchsenleiste J1 (8,5 mm) von unten einlöten, Lötstellen oben. Dazu 11-mm-Abstandshalter M2.5 (Pi 2/3/4/5). Mit dem Active Cooler des Pi 5 (ca. 13,7 mm hoch) eine 2×20-GPIO-Verlängerung mit 8,5 mm Körper dazwischen stecken, dann 19,5-mm-Abstandshalter verwenden.
- **XIAO-Modus**:
  - Den XIAO mit eingelöteten Stiftleisten verwenden (gibt es fertig gelötet). Er sitzt dann etwa 11 mm über der Platine. Sein USB-C zeigt nach links aus der Platine, Pin „5V“ und „D0“ sind auf der Platine markiert.
  - Vier Abstandshalter (M2.5, mindestens 10 mm) als Füße, weil die Buchse J1 auf der Unterseite 8,5 mm hoch ist.
- **Gehäuse**:
  - SHT40 (Insel unten rechts) und SGP41 brauchen frische Raumluft. Wenn möglich ein eigenes belüftetes Fach, getrennt von Pi oder XIAO.
  - Keine Schaumstoffe, Klebebänder oder Kleber in der Nähe des SGP41.
  - **Im Pi-Modus misst die Platine zu warm.** Ein Pi 4/5 heizt die Luft unter dem HAT, dann liegen Temperatur und Feuchte einige Grad daneben. Den Offset des SHT40 kalibrieren oder den HAT mit einem GPIO-Kabel abgesetzt betreiben. Im XIAO-Modus ist das deutlich weniger.
  - Kabel an J4/J5 nach außen (zum rechten Rand) wegführen, nicht über den Lichtsensor.
  - Kabel an J4/J5 kommen von oben, mit Kabelbogen etwa 25–28 mm Gesamthöhe über der Pi-Platine einplanen.
- **Feinstaubsensor**: 6-poliges JST-GH-Kabel, **Pin 1 auf Pin 1** (VDD). Vorher mit dem Multimeter prüfen, es gibt gekreuzte Kabel. Im XIAO-Modus SEN6x verwenden: Der SEN5x braucht mindestens 4,5 V, und die sind bei USB-Versorgung knapp.

## Lötbrücken

| Brücke | Auslieferzustand | Funktion |
|---|---|---|
| JP1 | offen | **Überbrücken = 3,3 V** an J3 Pin 1 (Radar LD2420/LD2410S) |
| JP3 | offen | **Überbrücken = 5 V** an J3 Pin 1 (LD2410C, LD2450, RCWL-0516). **Nie JP1 und JP3 zusammen.** |
| JP4 | **geschlossen** | 3,3 V an J4 für Sensirion **SEN6x** |
| JP5 | offen | 5 V an J4 für **SEN5x**: erst JP4 durchtrennen und nachmessen, dann JP5 brücken. **5 V zerstören einen SEN6x.** |
| JP6 | **1-2 geschlossen** | XIAO D5 = 1-Wire (J2). Für den Radar-OUT-Pin im XIAO-Modus: 1-2 durchtrennen, 2-3 brücken (dann kein 1-Wire). |
| JP2 | offen | Kurzschließen = HAT-EEPROM beschreibbar (nur Pi) |

## Radar-Sensor an J3

Die Pinfolge von J3 (V+, GND, TX des Moduls, RX des Moduls, OUT) passt direkt zu **HLK-LD2420** und **HLK-LD2410S** (3,3 V, JP1). LD2410C/LD2450 brauchen 5 V (JP3) und ein umgestecktes Kabel.

- Im XIAO-Modus:
  - LD2410/LD2410C über `software/esphome/sensor-hat-radar-ld2410.yaml` (5 V, umgestecktes Kabel)
  - LD2420 über die ESPHome-Komponente `ld2420`
  - den LD2410S unterstützt ESPHome nicht per UART, nutzbar ist nur sein OUT-Pin (JP6 2-3)
- Am Pi: OUT-Pin auf GPIO17, Daten per UART auf `/dev/ttyAMA0` (Pi 2).

## Inbetriebnahme am Raspberry Pi

1. Die Zeilen aus `software/config.txt.snippet` in `/boot/firmware/config.txt` übernehmen und neu starten.
2. Sensortest:
   ```bash
   python3 -m venv ~/hat && source ~/hat/bin/activate
   pip install adafruit-blinka adafruit-circuitpython-scd4x adafruit-circuitpython-sht4x \
       adafruit-circuitpython-veml7700 adafruit-circuitpython-neopixel-spi w1thermsensor gpiozero
   sudo ~/hat/bin/python3 software/sensor_test.py
   ```
3. SGP41 dauerhaft auswerten: `pip install sensirion-gas-index-algorithm`. Die Rohwerte des Testskripts jede Sekunde in `VocAlgorithm().process()` bzw. `NoxAlgorithm().process()` geben.
   - VOC-Index 1–500: 100 = Durchschnitt der letzten 24 h.
   - NOx-Index 1–500: 1 = Normalzustand, höhere Werte zeigen ein NOx-Ereignis (z. B. Gasherd).
4. SCD41: Ohne Barometer die Höhe des Wohnorts einstellen (`set_altitude`). Temperatur und Feuchte kommen vom SHT40; dessen Offset nach 15 Minuten gegen ein Referenzthermometer bestimmen.
5. Mikrofon: `arecord -D plughw:<Karte>,0 -c 2 -r 48000 -f S32_LE -d 5 test.wav`.

## Inbetriebnahme mit XIAO (ESPHome)

1. In Home Assistant das ESPHome-Add-on installieren oder ESPHome auf dem PC (`pip install esphome`).
2. Aus `software/esphome/` die passende Datei kopieren: `sensor-hat-xiao-s3.yaml`, `-c3.yaml` oder `-c6.yaml`. Dazu immer `sensor-hat-common.yaml` und eine `secrets.yaml` (Vorlage: `secrets.yaml.example`). Dort eintragen:
   - WLAN-Name und Passwort
   - einen API-Schlüssel (`openssl rand -base64 32`), er schützt auch die OTA-Updates
   - ein Passwort für den Notfall-Hotspot (mindestens 8 Zeichen)

   Mit den Platzhaltern aus der Vorlage bricht `esphome config` absichtlich ab. Bei mehreren Platinen jeder einen eigenen `name:` in den substitutions geben, z. B. `sensor-hat-kueche`.
3. XIAO **ohne Platine** per USB anschließen und einmal flashen. Danach in die Platine stecken, ab dann gehen Updates per WLAN. Beim Hinzufügen fragt Home Assistant nach dem API-Schlüssel.
4. In Home Assistant erscheinen CO₂, Temperatur, Feuchte, VOC/NOx, Helligkeit, Lautstärke (ungefähr dB SPL, unbewertet), Taster und LED. Die LED zeigt eine CO₂-Ampel: grün unter 1000 ppm, gelb ab 1000, rot ab 2000 (UBA-Richtwerte).
5. In `sensor-hat-common.yaml` `altitude_compensation` auf die Höhe deines Wohnorts setzen. Unter `sht4x` beim `offset`-Filter die Differenz zu einem Referenzthermometer eintragen (nach 15 Minuten Betrieb).
6. Radar (optional): `sensor-hat-radar-ld2410.yaml` unter `packages:` ergänzen.

Die Konfiguration ist mit ESPHome 2026.10 für S3, C3 und C6 geprüft (`esphome config`), die S3- und C3-Firmware wurde testweise kompiliert.

## ID-EEPROM programmieren (nur Pi, HAT+)

```bash
sudo apt install cmake git i2c-tools
(git clone https://github.com/raspberrypi/utils.git /tmp/rpi-utils && cd /tmp/rpi-utils/eeptools && cmake . && make && sudo make install)
eepmake software/eeprom_settings.txt sensorhat.eep     # erzeugte UUID in eeprom_settings.txt eintragen
# JP2 überbrücken (Schreibschutz aus)
sudo dtoverlay i2c-gpio i2c_gpio_sda=0 i2c_gpio_scl=1 bus=9
sudo eepflash.sh -w -t=24c32 -d=9 -a=50 -f=sensorhat.eep
# JP2 wieder öffnen, neu starten: cat /proc/device-tree/hat/product
```

## Projekt neu erzeugen

```bash
pip install easyeda2kicad
python3 -I scripts/fetch_3d_models.py .   # 3D-Modelle der LCSC-Bauteile (nur für 3D-Ansicht, Bilder, STEP)
export FREEROUTING_JAR=/pfad/zu/freerouting-2.5.0.jar
scripts/build.sh                 # Projekt, Schaltplan + ERC, Platine, Autorouting (6 Varianten), Masse-Reparatur, Aufräumen, DRC
python3 -I scripts/export.py .   # Gerber, Bohrdaten, BOM, CPL, PDFs, 3D-Bilder, STEP
python3 -I scripts/cost.py       # Kosten je Stückzahl mit Live-Preisen
```

Die Skripte erwarten KiCad unter macOS in `~/Applications/KiCad/KiCad.app`. Bei einer anderen Installation die Pfade oben in `build.sh`, `kicadlib.py`, `gen_pcb.py`, `route.py`, `cleanup.py` und `export.py` anpassen. Ist Java nicht das openjdk von Homebrew, vor `build.sh` `export JAVA=$(which java)` setzen.

Neue LCSC-Bauteile holen:

```bash
easyeda2kicad --full --lcsc_id=C123 --output /tmp/x/lib
python3 -I scripts/import_lcsc.py . /tmp/x
```

Benötigt KiCad 10, Java und Freerouting 2.5.

## Prüfstatus

- **KiCad-ERC**: 0 Verstöße. **KiCad-DRC** mit Schaltplanabgleich: 0 Verstöße, 0 offene Verbindungen, 0 Abweichungen.
- Masse vollständig verbunden. In1 ist eine geschlossene Massefläche. Alle Durchkontaktierungen sind 0,6/0,3 mm (JLCPCB-Standard für 4 Lagen).
- **Gegengeprüft** in drei getrennten KI-gestützten Review-Durchläufen (Elektrik und Firmware, Platine und Fertigung, Wärme/Mechanik/Doku), danach wurden die Befunde gegengeprüft. Ein Review durch eine Elektronik-Fachkraft gab es nicht. Geprüft wurden u. a.:
  - Pinbelegungen aller Bauteile gegen die Datenblätter
  - die Stromversorgung beider Betriebsarten
  - die XIAO-Boot-Pins
  - Footprints und JLCPCB-Drehungen gegen die LCSC-Footprints
  - Lagerbestand aller Teile
  - den Gerber-Satz
  
  Alle bestätigten Punkte sind eingearbeitet, unter anderem:
  - JP6-Beschriftung korrigiert
  - Gate-Kondensator C31 für den 5-V-Schalter
  - 0,5-W-Summer-Widerstand
  - breitere 5-V-Zuleitungen
  - Lotpaste unter dem SGP41
  - Schrift ≥ 1 mm
  - XIAO-Umriss
- ESPHome-Konfiguration für S3, C3 und C6 gültig (ESPHome 2026.10), S3- und C3-Firmware testweise kompiliert.

**Nicht in Hardware getestet.** Vor einer Sammelbestellung zuerst Prototypen bauen und messen.

## Lizenz

- **Hardware** (KiCad-Projekt, `design.py`/`placement.py`, Fertigungsdaten, PDFs, Bilder): CERN-OHL-S-2.0.
- **Software und Skripte**: MIT.
- **Dokumentation**: CC-BY-SA-4.0 oder, nach Wahl, CERN-OHL-S-2.0.

Wer die Platine oder die (auch veränderten) Entwurfsdaten weitergibt, muss die vollständigen Quelldaten unter derselben Lizenz mitgeben oder angeben, wo es sie gibt. Quelldaten: <https://github.com/Eniemooo/Sensor-HAT>. Einzelheiten stehen in [LICENSE.md](LICENSE.md). Einige Symbole und Footprints stammen aus der LCSC/EasyEDA-Bibliothek, für die keine eigene Lizenz angegeben ist. Diese Teile und die Marken stehen in [NOTICE.md](NOTICE.md). Keine Gewährleistung.

Raspberry Pi ist eine Marke der Raspberry Pi Ltd. Das Projekt steht in keiner Verbindung zu Raspberry Pi Ltd oder Seeed Studio.
