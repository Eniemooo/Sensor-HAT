# Sammelbestellung Sensor HAT v3: Ablauf und Regeln

Diese Anleitung beschreibt eine **einmalige, private Sammelbestellung zum Selbstkostenpreis** unter Bastlern. Sie ist keine Rechtsberatung. Wenn mehr als etwa 100 Platinen zusammenkommen oder weitere Runden geplant sind, vorher mit der IHK sprechen.

## Warum das günstiger wird

JLCPCB berechnet pro Bestellung feste Gebühren: Einrichtung, Schablone, jede Bauteilsorte, Versand. Bei 2 Platinen tragen 2 Platinen diese Kosten, bei 50 Platinen teilen sie sich auf 50. Zusätzlich werden einige Bauteile ab 10, 30 oder 100 Stück billiger.

Pro Platine, geliefert nach Deutschland inklusive 19 % MwSt. Die Werte sind geschätzt mit `scripts/cost.py`, Bauteilpreise live von JLCPCB am 22.10.2026; verbindlich ist das JLCPCB-Angebot.

| Platinen | Stiftleisten selbst löten | JLCPCB lötet auch J2, J3, J7, J8 (J1 immer selbst) |
|---|---|---|
| 5 (Pilot) | ca. 77 € | ca. 79 € |
| 10 | ca. 59 € | ca. 61 € |
| 20 | ca. 50 € | ca. 52 € |
| 50 | ca. 42 € | ca. 43 € |
| 100 | ca. 37 € | ca. 38 € |

Hinzu kommen je Teilnehmer etwa 2–6 € für den Versand innerhalb Deutschlands. Im XIAO-Betrieb braucht jeder außerdem einen Seeed XIAO ESP32-S3 (oder C3/C6) für etwa 8–10 €, den er selbst kauft.

## Regeln (vorher öffentlich ins Forum stellen)

1. **Einmalige Runde zum Selbstkostenpreis.** Kein Gewinn, keine Marge. Nach der Lieferung wird die JLCPCB-Rechnung mit der genauen Kostenaufteilung veröffentlicht. Adresse, Telefon, Bestell- und Kontonummern werden vorher geschwärzt.
2. **Du bestellst im eigenen Namen auf Rechnung der Teilnehmer.** Das ist ein unentgeltlicher Auftrag unter Privatleuten (§§ 662, 670 BGB), kein Verkauf. Die Platinen kommen so, wie JLCPCB sie liefert: ungetestetes Open-Hardware-Projekt, keine Gewährleistung. Das Risiko einzelner defekter Platinen tragen alle gemeinsam.
3. **Vorkasse per Überweisung** (nicht PayPal „Freunde“): Preis laut Tabelle plus 10 % Puffer für Wechselkurs, Zoll und Ausfälle. Der Rest wird nach der Lieferung zurücküberwiesen.
4. **Mindestmenge 20 bezahlte Teilnehmer.** Kommt die Mindestmenge in der Frist (3–4 Wochen) nicht zusammen, geht das Geld vollständig zurück.
5. **Nur die Platine.** Keine XIAO-Module, Akkus, Radar- oder Feinstaubsensoren mitbestellen. Funkmodule und Batterien hätten eigene gesetzliche Pflichten.
6. **Kein Marktplatz** (eBay, Kleinanzeigen, Tindie): Ab 30 Verkäufen oder 2.000 € meldet die Plattform ans Finanzamt (DAC7), und es sähe gewerblich aus.
7. **Datenschutz:** Erhoben werden nur Name, E-Mail, Lieferadresse und die Kontodaten aus der Überweisung.
   - Weitergegeben wird nur an Versanddienstleister und Bank.
   - Alles wird gelöscht, sobald Versand, Abrechnung und Rückzahlungen abgeschlossen sind.
   - Verantwortlich: [Name, E-Mail].
   - Rechtsgrundlage: Art. 6 Abs. 1 lit. b DSGVO (Durchführung der Sammelbestellung).
   - Rechte: Auskunft, Berichtigung, Löschung, Einschränkung der Verarbeitung und Datenübertragbarkeit, jederzeit per E-Mail.
   - Außerdem besteht ein Beschwerderecht bei einer Datenschutz-Aufsichtsbehörde, z. B. der des eigenen Bundeslands.

## Ablauf

| Schritt | Wann | Was |
|---|---|---|
| 1 | jetzt | Projekt offen veröffentlichen: GitHub oder Codeberg, Hardware CERN-OHL-S-2.0, Software MIT, Doku CC-BY-SA-4.0 oder CERN-OHL-S-2.0. Keine Provision nehmen: Ab 9.12.2026 gelten Konstruktionsdateien als Produkt, ausgenommen ist nur nicht-kommerzielle Open Source. |
| 2 | parallel | Prototyp: Sponsoring bei PCBWay und Elecrow anfragen (Vorlage in `docs/Sponsoring-Anfrage.md`). Ohne Zusage nach etwa 3 Wochen: 5er-Pilot mit 4 Testern aus den Foren teilen, ca. 77 € pro Person. |
| 3 | parallel | Unverbindlicher Interessenten-Aufruf (Text in `docs/Interessenten-Aufruf.md`) im Home-Assistant-Forum, bei simon42, auf mikrocontroller.net (Markt), r/homeassistant, r/raspberry_pi und Hackaday.io. Ziel: mindestens 40 Interessenten. |
| 4 | nach dem Prototyp | Inbetriebnahme, Messwerte veröffentlichen (CO₂ gegen Referenz, Temperatur-Offset), Fehler als v3.1 korrigieren. |
| 5 | Februar 2027 (nach dem chinesischen Neujahr) | Verbindliche Runde: Regeln posten, Vorkasse sammeln, Frist 3–4 Wochen. |
| 6 | sobald 20 bezahlt haben | Knappe Teile sofort bei JLCPCB reservieren (Private Parts Library): SCD41, SGP41, ICS-43434, JST-GH-Buchse. Dann eine einzige Bestellung (Standard PCBA, DHL DDP). |
| 7 | nach Lieferung | Jede Platine kurz prüfen (`i2cdetect` bzw. ESPHome-Log) und verschicken. Jeder Sendung den Link zum Repository (https://github.com/Eniemooo/Sensor-HAT) beilegen: Die CERN-OHL-S verlangt, dass Empfänger erfahren, wo die Quelldaten liegen. Danach Abrechnung veröffentlichen und Restbeträge zurücküberweisen. |

## Was du für die Bestellung brauchst

- `production/Sensor-HAT-gerber-jlcpcb.zip`, `Sensor-HAT-BOM-jlcpcb-komplett.csv`, `Sensor-HAT-CPL-jlcpcb-komplett.csv`. Bei „Stiftleisten selbst löten“ die Dateien ohne „komplett“ nehmen.
- Menge = Teilnehmer plus 1–2 Ersatzplatinen.
- Bemerkung an JLCPCB wie in README.de.md (Abschnitt „Bei JLCPCB bestellen“). Wichtig: Platine nicht waschen.

## Wenn es mehr wird

Melden sich deutlich mehr als 100 Leute, oder sollen weitere Runden folgen, ist das kein gelegentliches Bastlerprojekt mehr. Dann gibt es zwei Wege:

- **Eine Firma übernimmt Fertigung und Vertrieb**, z. B. Seeed Co-Create oder ein deutscher Pi-Shop. Für den Entwurf selbst erlaubt die CERN-OHL-S Fertigung und Verkauf. Die LCSC/EasyEDA-Bauteildaten deckt sie aber nicht ab (siehe `NOTICE.md`). Vorher also diese Teile durch Teile aus der KiCad-Bibliothek ersetzen oder eine Erlaubnis von LCSC einholen. Die Firma wird dann Hersteller und übernimmt CE, WEEE und Gewährleistung. Optional lässt sich die Nutzung des Projektnamens vereinbaren.
- **Selbst gewerblich werden:** Gewerbe, CE (EMV + RoHS), stiftung ear, Verpackungsregister, Produkthaftpflicht. Das kostet etwa 1.100–2.300 € einmalig und 400–850 € pro Jahr.
