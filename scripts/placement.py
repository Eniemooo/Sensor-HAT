# SPDX-FileCopyrightText: 2026 Emanuel Bachmann
# SPDX-License-Identifier: CERN-OHL-S-2.0
"""Board placement for the Sensor HAT v3 (mm, origin = top-left board corner, Y down).

v3: the XIAO socket (J7/J8) sits on the left edge with the USB-C pointing out of the board;
its series resistors, the 5 V ideal diode for the XIAO path and the SCD41 LDO sit underneath
it (parts < 8 mm tall). The middle (former RTC/CR1220 area) holds the 5 V switch, the J3
supply jumpers, the SGP41 and the light sensor; the SHT40 uses the milled island.

Board: 65 x 56 mm HAT (through-hole header variant), 40-pin header along the top,
pin 1 at (8.37, 4.77). Thermal notes (Pi 4/Pi 5 hot spots under the HAT): SoC
around (29..33, 24..33), PMIC around (10, 41..44), RP1/VL805 around (58, 20..32).
The coolest area is the bottom-right quadrant -> SHT40 on a slotted island there.
"""

# ref: (x, y, rotation_deg, side)
PLACE = {
    # Raspberry Pi header (kept exactly as in the KiCad HAT template, bottom side)
    "J1": (8.37, 4.77, -90, "B"),
    "MH1": (3.5, 3.5, 0, "F"), "MH2": (61.5, 3.5, 0, "F"),
    "MH3": (3.5, 52.5, 0, "F"), "MH4": (61.5, 52.5, 0, "F"),

    # power, top-left next to the 5 V pins (above the J8 socket row at y = 13.38)
    "U15": (6.2, 9.8, 0, "F"),       # ideal diode, Pi 5 V path, right at J1 pins 2/4
    "C30": (3.2, 8.6, 0, "F"),
    "R30": (3.2, 10.6, 0, "F"),
    "C11": (9.0, 9.4, 90, "F"),
    "C1": (11.2, 9.4, 90, "F"),
    "U5": (14.6, 9.6, 0, "F"),
    "C2": (18.0, 9.4, 90, "F"),
    "C13": (20.0, 9.4, 90, "F"),
    "TP1": (24.6, 13.0, 0, "F"),
    "TP2": (24.6, 9.6, 0, "F"),

    # XIAO socket: pin field centre (12.05, 21.0), USB-C out of the left edge.
    # J8 (5V, GND, 3V3, D10, D9, D8, D7) towards J1, J7 (D0..D6) towards J3; pin 1 at the USB end.
    "J8": (12.05, 13.38, 0, "F"),
    "J7": (12.05, 28.62, 0, "F"),
    # between the rows, under the XIAO (all parts < 8 mm): SCD41 LDO, XIAO 5 V ideal diode, EN OR
    "R7": (8.0, 18.7, 90, "F"),
    "C3": (11.2, 16.7, 90, "F"),
    "U6": (14.6, 16.9, 0, "F"),
    "C14": (18.0, 16.7, 90, "F"),
    "U14": (4.0, 18.5, 0, "F"),
    "C29": (4.0, 21.2, 0, "F"),
    "R29": (4.0, 22.8, 0, "F"),
    "D3": (10.0, 21.9, 0, "F"),
    "R43": (13.2, 21.9, 90, "F"),    # D10 -> LED_DATA
    "R42": (15.2, 21.9, 90, "F"),    # D9 -> SCL
    "R41": (17.2, 21.9, 90, "F"),    # D8 -> SDA
    "R40": (19.2, 21.9, 90, "F"),    # D7 -> UART_RX
    **{f"R{33 + i}": (4.43 + 2.54 * i, 25.7, 90, "F") for i in range(7)},   # D0..D6, one above each J7 pin
    # next to the XIAO's far end
    "JP6": (24.6, 25.0, 90, "F"),
    "R26": (24.6, 17.0, 90, "F"),
    "R27": (26.2, 17.0, 90, "F"),
    "R31": (24.6, 20.6, 90, "F"),
    "R32": (26.2, 20.6, 90, "F"),

    # ID EEPROM next to header pins 27/28 (x = 41.39)
    "U4": (40.6, 11.8, 0, "F"),
    "R2": (34.6, 9.0, 0, "F"),
    "R3": (34.6, 10.8, 0, "F"),
    "C10": (37.2, 10.4, 270, "F"),   # next to U4 pin 8
    "R5": (45.0, 13.4, 90, "F"),
    "JP2": (40.6, 17.6, 0, "F"),
    "TP5": (45.0, 17.6, 0, "F"),

    # microphone (bottom port) near I2S pins 35/38
    "U3": (55.0, 13.4, 0, "F"),
    "C9": (58.2, 11.8, 0, "F"),      # next to U3 VDD (pad 5)
    "R4": (58.6, 15.4, 90, "F"),

    # ambient light sensor, top view: > 21 mm from the 15 mm tall XIAO so it stays out of the 55 deg cone
    "U7": (46.5, 22.5, 0, "F"),
    "C8": (46.5, 25.2, 0, "F"),
    # VOC/NOx sensor, >= 16 mm from every LDO and 20 mm from the XIAO and the SHT40
    "U13": (42.5, 30.0, 0, "F"),
    "R28": (39.0, 28.8, 0, "F"),
    "C27": (39.0, 30.6, 0, "F"),
    "C28": (45.8, 30.0, 90, "F"),

    # CO2 sensor, bottom centre, far from the LDOs
    "U1": (30.0, 40.6, 0, "F"),
    "C4": (28.4, 33.8, 0, "F"),
    "C5": (28.0, 47.0, 180, "F"),    # under U1 pins 7/6
    "TP3": (22.4, 35.6, 0, "F"),

    # SHT40 on the thermally isolated island (bottom right)
    "U2": (50.0, 49.4, 0, "F"),
    "C6": (51.0, 47.3, 180, "F"),    # pad 1 (3V3) right, pad 2 (GND) left, both towards the neck
    "TP6": (37.0, 37.2, 0, "F"),
    "TP7": (40.0, 37.2, 0, "F"),
    "TP4": (38.0, 52.4, 0, "F"),

    # switched 5 V (LED, buzzer, J3/J4 5 V, J6) in the middle, former RTC area
    "F1": (32.0, 21.0, 90, "F"),
    "Q1": (35.0, 21.0, 0, "F"),
    "R14": (37.6, 21.0, 90, "F"),
    "C31": (39.3, 21.0, 90, "F"),     # Q1 gate-source cap
    "Q2": (35.0, 24.6, 0, "F"),
    "R15": (32.0, 25.0, 90, "F"),
    "C16": (37.6, 24.8, 90, "F"),
    "JP1": (33.0, 29.0, 0, "F"),
    "JP3": (33.0, 31.8, 0, "F"),
    "C12": (11.4, 31.6, 90, "F"),
    "R8": (18.4, 47.0, 90, "F"),     # series resistors right behind the ESD clamp
    "R9": (20.0, 47.0, 90, "F"),
    "R10": (21.6, 47.0, 90, "F"),
    "R11": (17.4, 33.8, 90, "F"),
    "R12": (19.2, 33.8, 90, "F"),
    "U8": (14.6, 48.0, 0, "F"),      # ESD clamp close to J3/J2
    "C15": (11.6, 48.0, 270, "F"),
    "R13": (9.8, 48.0, 90, "F"),
    "R1": (23.6, 44.2, 90, "F"),
    "R16": (23.6, 47.8, 90, "F"),

    # particulate-matter port with its own LDO, Qwiic and GPIO pads along the right edge
    "U9": (56.0, 21.0, 180, "F"),
    "C17": (53.6, 21.0, 90, "F"),
    "C18": (57.0, 24.4, 0, "F"),
    "C19": (57.2, 27.6, 90, "F"),
    "C20": (56.6, 31.2, 90, "F"),
    "JP4": (54.0, 36.6, 0, "F"),
    "JP5": (54.0, 39.6, 0, "F"),
    # J4/J5 are top-entry: side-entry plugs would point into the Pi's USB block (5 mm away, 16 mm tall)
    "J4": (61.5, 23.0, 90, "F"),
    "J5": (61.1, 32.0, 0, "F"),
    "J6": (59.3, 37.0, 0, "F"),

    # button, status LED (far corner from the light sensors) and buzzer, left side
    "SW1": (4.2, 38.4, 0, "F"),
    "R19": (9.0, 37.0, 90, "F"),
    "C23": (9.0, 40.2, 90, "F"),
    "D1": (3.0, 45.8, 0, "F"),
    "C24": (3.0, 43.6, 0, "F"),
    "U12": (7.0, 45.6, 0, "F"),
    "C26": (6.6, 42.4, 0, "F"),
    "R20": (4.6, 48.4, 0, "F"),
    "LS1": (14.6, 40.6, 0, "F"),
    "R21": (14.6, 36.6, 0, "F"),
    "D2": (14.6, 44.4, 0, "F"),
    "Q3": (20.0, 41.2, 0, "F"),
    "R22": (22.6, 38.8, 90, "F"),
    "R23": (20.0, 44.2, 0, "F"),

    # external headers along the bottom edge
    "J3": (9.0, 53.0, 90, "F"),
    "J2": (23.5, 53.0, 90, "F"),
}

# Hand-routed SHT40 island (F.Cu, 0.2 mm, locked), relative to U2 at rotation 0.
# Pads: 1 SDA (-0.7,-0.4), 2 SCL (-0.7,0.4), 3 VDD (0.7,0.4), 4 GND (0.7,-0.4). The footprint keeps
# every trace starts at its pad centre and leaves sideways (no copper under the package body).
# C6 at (1.0,-2.1), rotated 180: pad 1 (3V3) at (1.775,-2.1), pad 2 (GND) at (0.225,-2.1).
# All four traces leave through the neck (relative x -3.25..2.25 between the slot margins).
ISLAND_ORIGIN = (50.0, 49.4)
ISLAND_EXIT_Y = -10.0         # well above the slots, inside the main pour
# every pad centre and every junction is a segment end (Freerouting ignores T-joints)
ISLAND_TRACKS = [
    ("GND", 0.2, "F.Cu", [(0.7, -0.4), (1.1, -0.4), (1.1, -1.0), (0.225, -1.5), (0.225, -2.1)]),   # pad 4 -> C6.2
    ("GND", 0.2, "F.Cu", [(0.225, -2.1), (0.225, ISLAND_EXIT_Y)]),                                 # C6.2 -> exit
    ("+3V3", 0.2, "F.Cu", [(0.7, 0.4), (1.775, 0.4), (1.775, -2.1)]),                              # pad 3 -> C6.1
    ("+3V3", 0.2, "F.Cu", [(1.775, -2.1), (1.775, ISLAND_EXIT_Y)]),                                # C6.1 -> exit
    ("I2C_SDA", 0.2, "F.Cu", [(-0.7, -0.4), (-1.2, -0.4), (-1.2, ISLAND_EXIT_Y)]),
    ("I2C_SCL", 0.2, "F.Cu", [(-0.7, 0.4), (-1.9, 0.4), (-1.9, ISLAND_EXIT_Y - 1.0)]),
]
# the autorouter only connects to pads and vias, so the signal exits end on vias (staggered)
ISLAND_VIAS = [("GND", (0.225, ISLAND_EXIT_Y)), ("+3V3", (1.775, ISLAND_EXIT_Y)), ("I2C_SDA", (-1.2, ISLAND_EXIT_Y)),
               ("I2C_SCL", (-1.9, ISLAND_EXIT_Y - 1.0))]
# parts whose GND pads get no automatic fan-out via (island: thin traces only)
NO_FANOUT = {"U2", "C6"}

# SCD41: VDD (pin 7) and VDDH (pin 19) joined right at the sensor (datasheet 2.3): short stubs to
# vias just outside both pads and a straight 0.4 mm B.Cu link under the sensor (relative to U1, rot 0).
# The centre pad keeps its top-side connection to the GND pour.
SCD41_ORIGIN = (30.0, 40.6)
SCD41_TRACKS = [
    ("+3V3_CO2", 0.3, "F.Cu", [(-1.25, 4.0), (-1.25, 5.35)]),
    ("+3V3_CO2", 0.3, "F.Cu", [(-1.25, -4.0), (-1.25, -5.35)]),
    ("+3V3_CO2", 0.4, "B.Cu", [(-1.25, 5.35), (-1.25, -5.35)]),
]
SCD41_VIAS = [("+3V3_CO2", (-1.25, 5.35)), ("+3V3_CO2", (-1.25, -5.35))]

# J1 ground. Once the signals are routed, the pours no longer reach the GND pins of the
# header, so they get fixed copper: a GND bus along the top edge on F.Cu (via to both pours at
# each end) for the even-row pins 6/14/20/30/34, and a stub to a via below the header for the
# odd-row pins 9/25/39. Absolute board coordinates; the bus is split at every pin so all
# junctions are segment end points.
J1_GND_BUS_Y = 0.85
_J1_EVEN_GND_X = [13.45, 23.61, 31.23, 43.93, 49.01]
J1_GND_TRACKS = [("GND", 0.3, "F.Cu", [(7.1, 7.6), (7.1, J1_GND_BUS_Y)] + [(x, J1_GND_BUS_Y) for x in _J1_EVEN_GND_X]
                  + [(57.3, J1_GND_BUS_Y)])]
J1_GND_TRACKS += [("GND", 0.3, "F.Cu", [(x, J1_GND_BUS_Y), (x, 2.23)]) for x in _J1_EVEN_GND_X]
J1_GND_TRACKS += [("GND", 0.3, "F.Cu", [(x, 4.77), (x, 6.9)]) for x in (18.53, 38.85, 56.63)]
# +5V from both Pi 5 V pins (2 and 4): a short fixed link on B.Cu (the even row is boxed in on F.Cu)
J1_GND_TRACKS += [("+5V_PI", 0.6, "B.Cu", [(8.37, 2.23), (10.91, 2.23)])]
J1_GND_VIAS = [("GND", (7.1, 7.6)), ("GND", (57.3, J1_GND_BUS_Y)),
               ("GND", (18.53, 6.9)), ("GND", (38.85, 6.9)), ("GND", (56.63, 6.9))]

# reference designator positions (x, y, angle); None = footprint default
REF_POS = {}

# routed L-slots around the SHT40 island: centreline (end, corner, end), 1.2 mm wide (JLC min 1.0)
SLOT_W = 1.2
L_SLOTS = [
    ((42.8, 53.4), (42.8, 42.0), (46.0, 42.0)),   # left + top-left
    ((56.2, 53.4), (56.2, 42.0), (53.0, 42.0)),   # right + top-right (gap 46.6..52.4 for traces)
]

ISLAND = [(43.6, 42.8), (55.4, 42.8), (55.4, 55.6), (43.6, 55.6)]

# GND/3V3 pour outline (all layers): whole board minus the sensor island, so the island
# carries only thin traces and the autorouter knows there is no plane in it
POUR = [(0.4, 0.4), (64.6, 0.4), (64.6, 55.6), (55.4, 55.6), (55.4, 42.8),
        (43.6, 42.8), (43.6, 55.6), (0.4, 55.6)]


def circle(cx, cy, r, n=24):
    import math
    return [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n)) for i in range(n)]



def _slot_margins(margin=0.15):
    """Track/via keepouts slightly larger than the slots, so the autorouter keeps
    >= 0.35 mm to the routed edge (KiCad rule 0.3 mm)."""
    h = SLOT_W / 2 + margin
    out = []
    for p0, p1, p2 in L_SLOTS:
        for a, b in ((p0, p1), (p1, p2)):
            x0, x1 = sorted((a[0], b[0]))
            y0, y1 = sorted((a[1], b[1]))
            out.append([(x0 - h, y0 - h), (x1 + h, y0 - h), (x1 + h, y1 + h), (x0 - h, y1 + h)])
    return out


ALL_CU = ["F.Cu", "In1.Cu", "In2.Cu", "B.Cu"]

# silkscreen lines (F.Silkscreen): XIAO outline, open towards the USB-C board edge
SILK_LINES = [((5.0, 11.7), (22.8, 11.7)), ((22.8, 11.7), (22.8, 30.3))]

# rule areas: (name, layers, outline, {what is NOT allowed})
KEEPOUTS = [
    *[(f"slot-margin-{i}", ALL_CU, pts, {"tracks", "vias"}) for i, pts in enumerate(_slot_margins())],
    *[(f"mh{i + 1}", ALL_CU, circle(x, y, 3.2), {"zones", "tracks", "vias"})
      for i, (x, y) in enumerate([(3.5, 3.5), (61.5, 3.5), (3.5, 52.5), (61.5, 52.5)])],
    ("mic-port", ["In1.Cu", "In2.Cu", "B.Cu"], circle(55.0, 13.4 + 0.71, 0.95, 16), {"zones", "tracks", "vias"}),
    ("scd41-relief-hole", ALL_CU, circle(30.0 + 2.94, 40.6 + 2.94, 0.45, 12), {"vias"}),
    # no copper through the narrow bridges below the slot ends (edge clearance)
    ("bridge-left", ALL_CU, [(41.4, 53.0), (44.2, 53.0), (44.2, 56.0), (41.4, 56.0)], {"tracks", "vias", "zones"}),
    ("bridge-right", ALL_CU, [(54.8, 53.0), (57.6, 53.0), (57.6, 56.0), (54.8, 56.0)], {"tracks", "vias", "zones"}),
    # no pour in the neck between the slot tops either: only the four thin island traces cross it
    ("island-neck", ALL_CU, [(45.8, 40.4), (53.2, 40.4), (53.2, 43.0), (45.8, 43.0)], {"zones"}),
    # top side between the J1 rows is soldered by hand: no tracks there
    ("j1-rows", ["F.Cu"], [(7.45, 3.0), (58.0, 3.0), (58.0, 4.0), (7.45, 4.0)], {"tracks", "vias"}),
    ("pi5-poe", ["B.Cu"], [(58.5, 43.5), (64.5, 43.5), (64.5, 49.5), (58.5, 49.5)], {"footprints"}),
]

# silkscreen texts: (text, x, y, {size, angle, layer, bold, justify})
SILK = [
    ("1", 8.37, 7.0, {"size": 1.0}),
    ("3V3", 5.6, 7.0, {"size": 1.0}),
    ("V+", 9.0, 55.2, {"size": 1.0}),
    ("GND", 11.54, 55.2, {"size": 1.0}),
    ("RX", 14.08, 55.2, {"size": 1.0}),
    ("TX", 16.62, 55.2, {"size": 1.0}),
    ("IO17", 19.16, 55.2, {"size": 1.0}),
    ("GND", 23.5, 55.2, {"size": 1.0}),
    ("DQ", 26.04, 55.2, {"size": 1.0}),
    ("3V3", 28.58, 55.2, {"size": 1.0}),
    ("UART J3", 14.08, 51.0, {"size": 1.0}),
    ("1-WIRE J2", 26.04, 51.0, {"size": 1.0}),
    ("J3 VCC:", 31.0, 30.4, {"size": 1.0, "justify": "right"}),
    ("3V3", 35.0, 29.0, {"size": 1.0, "justify": "left"}),
    ("5V", 35.0, 31.8, {"size": 1.0, "justify": "left"}),
    ("XIAO USB-C", 1.0, 21.0, {"size": 1.0, "angle": 90}),
    ("5V", 1.7, 13.4, {"size": 1.0}),
    ("D0", 1.7, 28.6, {"size": 1.0}),
    ("NEVER XIAO + PI", 7.6, 34.6, {"size": 1.0}),
    ("RADAR", 26.4, 23.6, {"size": 1.0, "justify": "left"}),
    ("1W", 26.4, 26.4, {"size": 1.0, "justify": "left"}),
    # test point labels
    ("5V", 24.6, 14.9, {"size": 1.0}),
    ("3V3", 24.6, 7.7, {"size": 1.0}),
    ("CO2", 22.4, 33.7, {"size": 1.0}),
    ("GND", 38.0, 54.3, {"size": 1.0}),
    ("WP", 47.0, 17.6, {"size": 1.0, "justify": "left"}),
    ("SDA", 37.0, 39.1, {"size": 1.0}),
    ("SCL", 40.0, 39.1, {"size": 1.0}),
    ("BTN", 3.4, 42.0, {"size": 1.0}),
    ("3V3", 52.1, 36.6, {"size": 1.0, "justify": "right"}),
    ("5V", 52.1, 39.6, {"size": 1.0, "justify": "right"}),
    ("PM", 63.0, 16.6, {"size": 1.0}),
    ("QWIIC", 61.1, 34.95, {"size": 1.0}),
    # bottom side: title and legend (mirrored automatically)
    ("SENSOR HAT v3", 40.5, 9.8, {"size": 1.8, "bold": True, "layer": "B"}),
    ("SCD41 SHT40 SGP41 VEML7700 ICS-43434", 40.5, 12.2, {"size": 1.0, "layer": "B"}),
    ("Pi HAT or Seeed XIAO - never both", 40.5, 14.0, {"size": 1.0, "layer": "B"}),
    ("I2C 0x10 0x44 0x59 0x62 | PM 0x6B/0x69", 40.5, 15.7, {"size": 1.0, "layer": "B"}),
    ("JP4 closed = PM 3V3 (SEN6x)", 40.5, 17.5, {"size": 1.0, "layer": "B"}),
    ("cut JP4 + bridge JP5 = PM 5V (SEN5x)", 40.5, 19.2, {"size": 1.0, "layer": "B"}),
    ("J3 VCC: JP1 3V3 or JP3 5V, never both", 40.5, 21.0, {"size": 1.0, "layer": "B"}),
    ("JP2 short = EEPROM write", 40.5, 22.7, {"size": 1.0, "layer": "B"}),
    ("XIAO D0 LRCK D1 BCLK D2 MIC D3 BUZ", 40.5, 24.5, {"size": 1.0, "layer": "B"}),
    ("D4 BTN D5 1W/RADAR D6 TX D7 RX", 40.5, 26.2, {"size": 1.0, "layer": "B"}),
    ("D8 SDA D9 SCL D10 LED | USB-C >= 1.5 A", 40.5, 28.0, {"size": 1.0, "layer": "B"}),
    ("Pi: BTN 27 LED 10 BUZ 13 1W 4 RADAR 17", 40.5, 29.7, {"size": 1.0, "layer": "B"}),
    ("J6 (Pi): 1 3V3 2 5V 3 IO5 4 IO12 5 IO22", 40.5, 31.5, {"size": 1.0, "layer": "B"}),
    ("6 IO23 7 IO24 8 IO25 9 IO26 10 GND", 40.5, 33.2, {"size": 1.0, "layer": "B"}),
]
