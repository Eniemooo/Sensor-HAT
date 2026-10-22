# SPDX-FileCopyrightText: 2026 Emanuel Bachmann
# SPDX-License-Identifier: CERN-OHL-S-2.0
"""Single source of truth for the Sensor HAT v3 "Universal": parts, nets, schematic positions.

v3 runs either as a HAT for Raspberry Pi or standalone with a user-supplied Seeed XIAO
(ESP32-S3/C3/C6) in the J7/J8 socket. Never both hosts at once.

Both gen_sch.py (schematic) and gen_pcb.py (board) read this file, so the
schematic and the PCB cannot drift apart. LCSC numbers and stock were checked
against the JLCPCB parts API on 2026-10-21.
"""
import uuid

PROJECT = "Sensor-HAT"
TITLE = "Sensor HAT v3 Universal (for Raspberry Pi or Seeed XIAO)"
REV = "3.0"
DATE = "2026-10-22"
AUTHOR = "Emanuel Bachmann"
NAMESPACE = uuid.UUID("6f1d2c3a-1b2c-4d5e-8f90-a1b2c3d4e5f6")

R0603 = "Resistor_SMD:R_0603_1608Metric"
C0603 = "Capacitor_SMD:C_0603_1608Metric"
C0805 = "Capacitor_SMD:C_0805_2012Metric"


def R(ref, value, a, b, lcsc, mpn, sch, desc=""):
    return dict(ref=ref, sym="Device:R", value=value, fp=R0603, LCSC=lcsc, MPN=mpn,
                Manufacturer="UNI-ROYAL", pins={"1": a, "2": b}, sch=sch, desc=desc)


def C(ref, value, a, b, lcsc, mpn, sch, fp=C0603, mfr="Samsung", desc=""):
    # pin 1 = supply side, pin 2 = GND
    return dict(ref=ref, sym="Device:C", value=value, fp=fp, LCSC=lcsc, MPN=mpn,
                Manufacturer=mfr, pins={"1": a, "2": b}, sch=sch, desc=desc)


def C100n(ref, net, sch, desc=""):
    return C(ref, "100nF", net, "GND", "C14663", "CC0603KRX7R9BB104", sch, mfr="YAGEO", desc=desc)


def C1u(ref, net, sch, desc=""):
    return C(ref, "1uF", net, "GND", "C15849", "CL10A105KB8NNNC", sch, desc=desc)


def C10u(ref, net, sch, desc=""):
    return C(ref, "10uF", net, "GND", "C19702", "CL10A106KP8NNNC", sch, desc=desc)


def C10u25(ref, net, sch, desc=""):
    return C(ref, "10uF 25V", net, "GND", "C15850", "CL21A106KAYNNNE", sch, fp=C0805, desc=desc)


# Raspberry Pi 40-pin header (J1): pin -> net
# hand=True: not in the SMD-only JLC files; jlc_rot turns the KiCad orientation into the
# JLC/EasyEDA one (row horizontal, pin 1 left) for the full-assembly variant.
J1_PINS = {
    "1": "+3V3_PI", "17": "+3V3_PI",
    "2": "+5V_PI", "4": "+5V_PI",
    "3": "I2C_SDA", "5": "I2C_SCL",
    "7": "ONEWIRE",
    "8": "UART_TX", "10": "UART_RX", "11": "GPIO17",
    "12": "I2S_BCLK", "35": "I2S_LRCLK", "38": "I2S_DIN",
    "27": "ID_SD", "28": "ID_SC",
    # user interface
    "13": "BTN",          # GPIO27  push-button
    "19": "LED_DATA",     # GPIO10  SPI0 MOSI -> WS2812 status LED
    "33": "BUZ_PWM",      # GPIO13  PWM1 -> buzzer
    # spare GPIOs on the J6 expansion pads
    "29": "GPIO5", "32": "GPIO12", "15": "GPIO22", "16": "GPIO23",
    "18": "GPIO24", "22": "GPIO25", "37": "GPIO26",
}
for _p in ("6", "9", "14", "20", "25", "30", "34", "39"):
    J1_PINS[_p] = "GND"

PARTS = [
    # ---------------- Raspberry Pi header ----------------
    dict(ref="J1", sym="Connector_Generic:Conn_02x20_Odd_Even", value="RPi GPIO 2x20",
         fp="Connector_PinSocket_2.54mm:PinSocket_2x20_P2.54mm_Vertical",
         LCSC="C2977589", MPN="2.54-2*20", Manufacturer="ZHOURI", hand=True, hand_only=True, jlc_rot=90,
         pins=J1_PINS, sch=(50.8, 101.6), desc="Raspberry Pi 40-pin GPIO header (female, 8.5 mm, bottom side)"),

    # ---------------- Power ----------------
    dict(ref="U5", sym="Regulator_Linear:AP2112K-3.3", value="AP2112K-3.3",
         fp="SensorHAT:SOT-25-5_L2.9-W1.6-P0.95-LS2.8-BL",
         LCSC="C51118", MPN="AP2112K-3.3TRG1", Manufacturer="Diodes",
         pins={"1": "+5V", "2": "GND", "3": "LDO_EN", "5": "+3V3"}, sch=(157.48, 58.42),
         desc="3.3 V LDO for SHT40, SGP41, VEML7700, mic, pull-ups, Qwiic, 1-Wire, UART"),
    dict(ref="U6", sym="Regulator_Linear:AP2112K-3.3", value="AP2112K-3.3",
         fp="SensorHAT:SOT-25-5_L2.9-W1.6-P0.95-LS2.8-BL",
         LCSC="C51118", MPN="AP2112K-3.3TRG1", Manufacturer="Diodes",
         pins={"1": "+5V", "2": "GND", "3": "LDO_EN", "5": "+3V3_CO2"}, sch=(157.48, 96.52),
         desc="Separate 3.3 V LDO for SCD41 (Sensirion recommendation)"),
    C10u25("C11", "+5V", (109.22, 60.96), desc="5 V bulk at header"),
    C1u("C1", "+5V", (127.0, 60.96), desc="U5 input"),
    C1u("C2", "+3V3", (187.96, 60.96), desc="U5 output"),
    C10u("C13", "+3V3", (205.74, 60.96), desc="3.3 V bulk"),
    C1u("C3", "+5V", (127.0, 99.06), desc="U6 input"),
    C1u("C14", "+3V3_CO2", (187.96, 99.06), desc="U6 output"),
    dict(ref="D3", sym="SensorHAT:BAV70-C68978", value="BAV70", fp="SensorHAT:SOT-23-3_L3.0-W1.7-P0.95-LS2.9-BR",
         LCSC="C68978", MPN="BAV70", Manufacturer="CJ",
         pins={"1": "+3V3_PI", "2": "+3V3_XIAO", "3": "LDO_EN"}, sch=(119.38, 132.08),
         desc="Enable OR: LDOs and 5 V switch on while the Pi 3V3 OR the XIAO 3V3 is up (HAT+ standby kept)"),
    # 5 V: TI dual ideal-diode ORing (LM66100 datasheet 9.2.1), each CE on the other source
    dict(ref="U15", sym="SensorHAT:LM66100DCKR", value="LM66100", fp="SensorHAT:SC-70-6_L2.0-W1.3-P0.65-LS2.1-BL",
         LCSC="C2869734", MPN="LM66100DCKR", Manufacturer="TI",
         pins={"1": "+5V_PI", "2": "GND", "3": "+5V_XIAO", "4": "GND", "5": "GND", "6": "+5V"}, sch=(210.82, 314.96),
         desc="Ideal diode, Pi 5 V path (off while the XIAO supplies 5 V, no back-feed into the Pi)"),
    C1u("C30", "+5V_PI", (190.5, 320.04), desc="U15 input"),
    R("R30", "100k", "+5V_PI", "GND", "C25803", "0603WAF1003T5E", (180.34, 320.04),
      desc="Holds +5V_PI low without a Pi so U14 CE is defined"),
    dict(ref="U14", sym="SensorHAT:LM66100DCKR", value="LM66100", fp="SensorHAT:SC-70-6_L2.0-W1.3-P0.65-LS2.1-BL",
         LCSC="C2869734", MPN="LM66100DCKR", Manufacturer="TI",
         pins={"1": "+5V_XIAO", "2": "GND", "3": "+5V_PI", "4": "GND", "5": "GND", "6": "+5V"}, sch=(210.82, 345.44),
         desc="Ideal diode, XIAO USB 5 V path (off while a Pi supplies 5 V, no back-feed into USB)"),
    C1u("C29", "+5V_XIAO", (190.5, 350.52), desc="U14 input"),
    R("R29", "100k", "+5V_XIAO", "GND", "C25803", "0603WAF1003T5E", (180.34, 350.52),
      desc="Holds +5V_XIAO low without a XIAO so U15 CE is defined"),
    R("R7", "100k", "LDO_EN", "GND", "C25803", "0603WAF1003T5E", (139.7, 132.08), desc="LDO enable pull-down"),
    dict(ref="#FLG01", sym="power:PWR_FLAG", value="PWR_FLAG", pins={"1": "GND"}, sch=(106.68, 33.02)),
    dict(ref="#FLG02", sym="power:PWR_FLAG", value="PWR_FLAG", pins={"1": "+5V"}, sch=(127.0, 33.02)),
    dict(ref="#FLG03", sym="power:PWR_FLAG", value="PWR_FLAG", pins={"1": "+3V3_PI"}, sch=(147.32, 33.02)),

    # ---------------- I2C sensors ----------------
    dict(ref="U1", sym="Sensor_Gas:SCD41-D-R2", value="SCD41-D-R2",
         fp="SensorHAT:LGA-20_L10.1-W10.1-P1.25-TL_SCD41-D-R2",
         LCSC="C3659294", MPN="SCD41-D-R2", Manufacturer="Sensirion",
         pins={"6": "GND", "20": "GND", "21": "GND", "7": "+3V3_CO2", "19": "+3V3_CO2",
               "9": "I2C_SCL", "10": "I2C_SDA"},
         sch=(264.16, 66.04), desc="CO2 sensor, I2C 0x62"),
    C10u("C4", "+3V3_CO2", (233.68, 60.96), desc="SCD41 bulk for 205 mA pulses"),
    C100n("C5", "+3V3_CO2", (246.38, 60.96), desc="SCD41 VDD/VDDH"),
    dict(ref="U2", sym="Sensor_Humidity:SHT4x", value="SHT40",
         fp="SensorHAT:SHT4x_DFN-4_1.5x1.5mm_P0.8mm_NoCentralPad",
         LCSC="C2909890", MPN="SHT40-AD1B-R2", Manufacturer="Sensirion",
         pins={"1": "I2C_SDA", "2": "I2C_SCL", "3": "+3V3", "4": "GND"},
         sch=(337.82, 71.12), desc="Temperature/humidity on the milled island, I2C 0x44 (no copper under the die)"),
    C100n("C6", "+3V3", (373.38, 50.8), desc="SHT40 VDD"),
    dict(ref="U13", sym="SensorHAT:SGP41-D-R4", value="SGP41",
         fp="SensorHAT:DFN-6_L2.4-W2.4-P0.80-TL-EP",
         LCSC="C3659325", MPN="SGP41-D-R4", Manufacturer="Sensirion",
         pins={"1": "SGP_VDD", "2": "GND", "3": "I2C_SDA", "4": "GND", "5": "+3V3", "6": "I2C_SCL", "7": "GND"},
         sch=(347.98, 320.04), desc="VOC + NOx index (open gas-index algorithm), I2C 0x59"),
    R("R28", "4.7", "+3V3", "SGP_VDD", "C23164", "0603WAF470KT5E", (325.12, 309.88),
      desc="SGP41 VDD RC filter (datasheet Fig. 6)"),
    C1u("C27", "SGP_VDD", (370.84, 309.88), desc="SGP41 VDD"),
    C1u("C28", "+3V3", (383.54, 309.88), desc="SGP41 VDDH (hotplate supply)"),
    dict(ref="U7", sym="SensorHAT:VEML7700-TT", value="VEML7700-TT",
         fp="SensorHAT:SENSOR-SMD_EML7700-TT",
         LCSC="C1850416", MPN="VEML7700-TT", Manufacturer="Vishay",
         pins={"1": "I2C_SCL", "2": "+3V3", "3": "GND", "4": "I2C_SDA"},
         sch=(264.16, 124.46), desc="Ambient light sensor (top view), I2C 0x10"),
    C100n("C8", "+3V3", (233.68, 121.92), desc="VEML7700 VDD"),

    # ---------------- Microphone ----------------
    dict(ref="U3", sym="Sensor_Audio:ICS-43434", value="ICS-43434",
         fp="Sensor_Audio:InvenSense_ICS-43434-6_3.5x2.65mm",
         LCSC="C5656610", MPN="ICS-43434", Manufacturer="TDK InvenSense",
         pins={"1": "I2S_LRCLK", "2": "GND", "3": "GND", "4": "I2S_BCLK", "5": "+3V3", "6": "I2S_DIN"},
         sch=(345.44, 124.46), jlc_rot=-90,
         desc="I2S MEMS microphone (bottom port), left channel"),
    C100n("C9", "+3V3", (322.58, 114.3), desc="Mic VDD"),
    R("R4", "100k", "I2S_DIN", "GND", "C25803", "0603WAF1003T5E", (373.38, 134.62), desc="I2S SD pull-down"),

    # ---------------- ID EEPROM ----------------
    dict(ref="U4", sym="Memory_EEPROM:24LC32", value="CAT24C32",
         fp="SensorHAT:SOIC-8_L5.0-W4.0-P1.27-LS6.0-BL",
         LCSC="C81193", MPN="CAT24C32WI-GT3", Manufacturer="onsemi",
         pins={"1": "GND", "2": "GND", "3": "GND", "4": "GND", "5": "ID_SD", "6": "ID_SC",
               "7": "EE_WP", "8": "+3V3_PI"},
         sch=(76.2, 210.82), desc="HAT+ ID EEPROM, address 0x50 on ID_SD/ID_SC"),
    C100n("C10", "+3V3_PI", (50.8, 190.5), desc="EEPROM VCC"),
    R("R2", "3.9k", "+3V3_PI", "ID_SC", "C23018", "0603WAF3901T5E", (106.68, 195.58), desc="ID_SC pull-up (HAT+ spec)"),
    R("R3", "3.9k", "+3V3_PI", "ID_SD", "C23018", "0603WAF3901T5E", (121.92, 195.58), desc="ID_SD pull-up (HAT+ spec)"),
    R("R5", "1k", "+3V3_PI", "EE_WP", "C21190", "0603WAF1001T5E", (50.8, 233.68), desc="WP pull-up = write protected"),
    dict(ref="JP2", sym="Jumper:SolderJumper_2_Open", value="EEPROM write enable",
         fp="Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm",
         pins={"1": "EE_WP", "2": "GND"}, sch=(78.74, 243.84), no_bom=True,
         desc="Bridge to allow writing the ID EEPROM"),

    # ---------------- 1-Wire ----------------
    dict(ref="J2", sym="Connector_Generic:Conn_01x03", value="1-Wire GND/DQ/3V3",
         fp="Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical",
         LCSC="C49257", MPN="2.54-1*3P", Manufacturer="BOOMELE", hand=True, jlc_rot=-90,
         pins={"1": "GND", "2": "ONEWIRE_EXT", "3": "+3V3"}, sch=(195.58, 200.66),
         desc="DS18B20 header, same pin order as the TO-92 package (GND, DQ, VDD)"),
    R("R1", "4.7k", "+3V3", "ONEWIRE", "C23162", "0603WAF4701T5E", (170.18, 195.58), desc="1-Wire pull-up"),
    R("R16", "100", "ONEWIRE_EXT", "ONEWIRE", "C22775", "0603WAF1000T5E", (182.88, 220.98),
      desc="1-Wire series (ESD current limit into GPIO4)"),

    # ---------------- UART + switched 5 V ----------------
    dict(ref="J3", sym="Connector_Generic:Conn_01x05", value="UART (e.g. PMS5003)",
         fp="Connector_PinHeader_2.54mm:PinHeader_1x05_P2.54mm_Vertical",
         LCSC="C32713271", MPN="HX PZ2.54-1x5P ZZ", Manufacturer="hanxia", hand=True, jlc_rot=-90,
         pins={"1": "UART_VCC", "2": "GND", "3": "UART_RX_EXT", "4": "UART_TX_EXT", "5": "GPIO17_EXT"},
         sch=(398.78, 220.98),
         desc="1 V+ (JP1 3.3 V or JP3 5 V) 2 GND 3 RX of Pi (to device TX) 4 TX of Pi (to device RX) 5 GPIO17"),
    R("R8", "1k", "UART_TX", "UART_TX_EXT", "C21190", "0603WAF1001T5E", (337.82, 223.52), desc="series, Pi TXD"),
    R("R9", "1k", "UART_RX_EXT", "UART_RX", "C21190", "0603WAF1001T5E", (350.52, 223.52),
      desc="series, Pi RXD; small so a device low stays < 0.2 V against R11 and the Pi pad pull-up"),
    R("R10", "1k", "GPIO17", "GPIO17_EXT", "C21190", "0603WAF1001T5E", (363.22, 223.52), desc="series, GPIO17"),
    R("R11", "100k", "+3V3", "UART_RX", "C25803", "0603WAF1003T5E", (312.42, 200.66),
      desc="RXD idle-high pull-up; must stay >> R9 (1k series)"),
    R("R12", "10k", "+3V3", "GPIO17", "C25804", "0603WAF1002T5E", (325.12, 200.66),
      desc="GPIO17 defined high level (beats the ~50k pad pull-down)"),
    dict(ref="U8", sym="Power_Protection:SRV05-4", value="SRV05-4",
         fp="SensorHAT:SOT-23-6_L2.9-W1.6-P0.95-LS2.8-BR",
         LCSC="C85364", MPN="SRV05-4-P-T7", Manufacturer="ProTek Devices",
         pins={"1": "ONEWIRE_EXT", "2": "GND", "3": "UART_TX_EXT", "4": "UART_RX_EXT", "5": "ESD_REF",
               "6": "GPIO17_EXT"},
         sch=(190.5, 238.76), desc="ESD protection for the external header signals"),
    R("R13", "100k", "+3V3", "ESD_REF", "C25803", "0603WAF1003T5E", (220.98, 231.14),
      desc="ESD reference via 100k (limits back-feed)"),
    C1u("C15", "ESD_REF", (233.68, 236.22), desc="ESD reference reservoir"),
    dict(ref="F1", sym="Device:Polyfuse", value="0.5A PTC", fp="Fuse:Fuse_1206_3216Metric",
         LCSC="C70077", MPN="nSMD050-33V", Manufacturer="TECHFUSE",
         pins={"1": "+5V", "2": "+5V_FUSED"}, sch=(241.3, 200.66), desc="Resettable fuse for the UART 5 V"),
    dict(ref="Q1", sym="Transistor_FET:AO3401A", value="AO3401A",
         fp="SensorHAT:SOT-23_L2.9-W1.3-P1.90-LS2.4-BR",
         LCSC="C15127", MPN="AO3401A", Manufacturer="Alpha & Omega",
         pins={"1": "Q1_G", "2": "+5V_FUSED", "3": "+5V_SW"}, sch=(269.24, 195.58),
         desc="High-side switch: switched 5 V only while a host (Pi or XIAO) is on"),
    dict(ref="Q2", sym="SensorHAT:AO3400A", value="AO3400A",
         fp="SensorHAT:SOT-23_L2.9-W1.3-P1.90-LS2.4-BR",
         LCSC="C20917", MPN="AO3400A", Manufacturer="Alpha & Omega",
         pins={"1": "LDO_EN", "2": "GND", "3": "Q2_D"}, sch=(266.7, 228.6),
         desc="Q1 gate driver (Vth max 1.45 V: LDO_EN is only ~2.7 V behind the BAV70)"),
    R("R15", "10k", "Q2_D", "Q1_G", "C25804", "0603WAF1002T5E", (284.48, 215.9), desc="Q1 gate series (soft start)"),
    C("C16", "100nF", "Q1_G", "+5V_SW", "C14663", "CC0603KRX7R9BB104", (297.18, 215.9), mfr="YAGEO",
      desc="Q1 Miller capacitor: ~1.4 ms soft start, keeps the inrush off the XIAO USB"),
    R("R14", "100k", "+5V_FUSED", "Q1_G", "C25803", "0603WAF1003T5E", (248.92, 218.44), desc="Q1 gate pull-up (off)"),
    C("C31", "1uF", "+5V_FUSED", "Q1_G", "C15849", "CL10A105KB8NNNC", (248.92, 238.76),
      desc="Q1 gate-source cap: keeps Q1 off while +5V ramps up (C16 alone would let +5V_SW follow)"),
    dict(ref="JP1", sym="Jumper:SolderJumper_2_Open", value="J3 VCC = 3V3",
         fp="Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm",
         pins={"1": "+3V3", "2": "UART_VCC"}, sch=(302.26, 172.72), no_bom=True,
         desc="Bridge for 3.3 V on J3 pin 1 (bridge JP1 OR JP3, never both)"),
    dict(ref="JP3", sym="Jumper:SolderJumper_2_Open", value="J3 VCC = 5V",
         fp="Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm",
         pins={"1": "+5V_SW", "2": "UART_VCC"}, sch=(302.26, 185.42), no_bom=True,
         desc="Bridge for switched, fused 5 V on J3 pin 1 (bridge JP1 OR JP3, never both)"),
    C10u25("C12", "UART_VCC", (325.12, 177.8), desc="UART device supply bulk"),


    # ---------------- Particulate-matter port (Sensirion SEN6x 3.3 V / SEN5x 5 V, I2C) ----------------
    dict(ref="U9", sym="Regulator_Linear:AP2112K-3.3", value="AP2112K-3.3",
         fp="SensorHAT:SOT-25-5_L2.9-W1.6-P0.95-LS2.8-BL",
         LCSC="C51118", MPN="AP2112K-3.3TRG1", Manufacturer="Diodes",
         pins={"1": "+5V", "2": "GND", "3": "LDO_EN", "5": "+3V3_PM"}, sch=(76.2, 317.5),
         desc="Own 3.3 V LDO for the PM sensor (fan current pulses stay off the sensor rails)"),
    C1u("C17", "+5V", (50.8, 320.04), desc="U9 input"),
    C1u("C18", "+3V3_PM", (101.6, 320.04), desc="U9 output"),
    dict(ref="JP4", sym="Jumper:SolderJumper_2_Bridged", value="PM VCC = 3V3",
         fp="Jumper:SolderJumper-2_P1.3mm_Bridged_RoundedPad1.0x1.5mm",
         pins={"1": "+3V3_PM", "2": "PM_VCC"}, sch=(127.0, 309.88), no_bom=True,
         desc="Closed by default: 3.3 V for SEN6x. Cut it (and bridge JP5) only for SEN5x"),
    dict(ref="JP5", sym="Jumper:SolderJumper_2_Open", value="PM VCC = 5V",
         fp="Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm",
         pins={"1": "+5V_SW", "2": "PM_VCC"}, sch=(127.0, 325.12), no_bom=True,
         desc="Bridge only for 5 V SEN5x after cutting JP4. 5 V destroys a SEN6x"),
    C("C19", "22uF 25V", "PM_VCC", "GND", "C45783", "CL21A226MAQNNNE", (149.86, 345.44), fp=C0805,
      desc="PM sensor bulk (350 mA / 2 ms pulses)"),
    C100n("C20", "PM_VCC", (162.56, 345.44), desc="PM sensor decoupling"),
    dict(ref="J4", sym="SensorHAT:BM06B-GHS-TBT", value="PM sensor (SEN6x/SEN5x)",
         fp="SensorHAT:CONN-SMD_6P-P1.25_BM06B-GHS-TBT-LF-SN-N",
         LCSC="C189892", MPN="BM06B-GHS-TBT(LF)(SN)", Manufacturer="JST",
         pins={"1": "PM_VCC", "2": "GND", "3": "I2C_SDA", "4": "I2C_SCL", "5": "GND", "7": "GND", "8": "GND"},
         sch=(172.72, 317.5),
         desc="JST GH 6-pin, vertical (cable from above, clear of the Pi USB/RJ45): 1 VDD, 2 GND, 3 SDA, 4 SCL, 5 GND (SEN5x SEL), 6 NC. SEN6x 0x6B, SEN5x 0x69"),

    # ---------------- Expansion ----------------
    dict(ref="J5", sym="SensorHAT:BM04B-SRSS-TB", value="Qwiic / STEMMA QT",
         fp="SensorHAT:CONN-SMD_BM04B-SRSS-TB",
         LCSC="C160390", MPN="BM04B-SRSS-TB(LF)(SN)", Manufacturer="JST",
         pins={"1": "GND", "2": "+3V3", "3": "I2C_SDA", "4": "I2C_SCL", "5": "GND", "6": "GND"},
         sch=(403.86, 317.5), desc="Qwiic, vertical JST SH: 1 GND, 2 3V3, 3 SDA, 4 SCL (3.3 V only)"),
    dict(ref="J6", sym="Connector_Generic:Conn_02x05_Odd_Even", value="GPIO expansion (DNP)",
         fp="Connector_PinHeader_2.54mm:PinHeader_2x05_P2.54mm_Vertical",
         pins={"1": "+3V3", "2": "+5V_SW", "3": "GPIO5", "4": "GPIO12", "5": "GPIO22", "6": "GPIO23",
               "7": "GPIO24", "8": "GPIO25", "9": "GPIO26", "10": "GND"},
         sch=(449.58, 322.58), no_bom=True, dnp=True,
         desc="Unpopulated 2x5 pads: free GPIOs plus 3V3 / switched 5V / GND"),

    # ---------------- Button, status LED, buzzer ----------------
    dict(ref="SW1", sym="SensorHAT:TS-1187A-B-A-B", value="Button",
         fp="SensorHAT:SW-SMD_4P-L5.1-W5.1-P3.70-LS6.5-TL_H1.5",
         LCSC="C318884", MPN="TS-1187A-B-A-B", Manufacturer="XKB",
         pins={"1": "BTN", "2": "BTN", "3": "GND", "4": "GND"}, sch=(495.3, 320.04),
         desc="User button on GPIO27 (pads 1-2 and 3-4 are internally connected)"),
    R("R19", "10k", "+3V3", "BTN", "C25804", "0603WAF1002T5E", (520.7, 309.88), desc="Button pull-up (GPIO27 defaults to pull-down)"),
    C100n("C23", "BTN", (533.4, 330.2), desc="Button debounce"),
    dict(ref="U12", sym="SensorHAT:SN74LV1T125DBVR", value="74LV1T125",
         fp="SensorHAT:SOT-23-5_L3.0-W1.7-P0.95-LS2.8-BL",
         LCSC="C473338", MPN="SN74LV1T125DBVR", Manufacturer="TI",
         pins={"1": "GND", "2": "LED_DATA", "3": "GND", "4": "LED_BUF", "5": "+5V_SW"}, sch=(279.4, 375.92),
         desc="3.3 V -> 5 V level shift for the WS2812 data line"),
    C100n("C26", "+5V_SW", (254.0, 368.3), desc="U12 VCC"),
    R("R20", "100", "LED_BUF", "LED_DIN", "C22775", "0603WAF1000T5E", (309.88, 381.0), desc="WS2812 data series resistor"),
    R("R32", "100k", "LED_DATA", "GND", "C25803", "0603WAF1003T5E", (264.16, 393.7),
      desc="Keeps the buffer input defined (LED dark) while no host drives it"),
    dict(ref="D1", sym="SensorHAT:WS2812B-2020-V6", value="WS2812B-2020",
         fp="SensorHAT:LED-SMD_4P-L2.2-W2.0-P1.00_WS2815C-2020-4P",
         LCSC="C52917434", MPN="WS2812B-2020-V6", Manufacturer="Worldsemi",
         pins={"2": "GND", "3": "LED_DIN", "4": "+5V_SW"}, sch=(337.82, 378.46),
         desc="RGB status LED (e.g. CO2 traffic light); switch off during light measurements"),
    C100n("C24", "+5V_SW", (360.68, 368.3), desc="WS2812 VDD"),
    dict(ref="LS1", sym="SensorHAT:MLT-5020", value="MLT-5020 4kHz",
         fp="SensorHAT:BUZ-SMD_L5.0-W5.5-P4.60",
         LCSC="C94598", MPN="MLT-5020", Manufacturer="Huaneng",
         pins={"1": "BUZ_P", "2": "BUZ_N"}, sch=(406.4, 375.92),
         desc="Magnetic buzzer 12 ohm, 3 Vp-p; drive with 4 kHz PWM, 50 %"),
    dict(ref="R21", sym="Device:R", value="33 0.5W 1206", fp="Resistor_SMD:R_1206_3216Metric",
         LCSC="C5713420", MPN="FRP1206F33R0TS", Manufacturer="FOJAN",
         pins={"1": "+5V_SW", "2": "BUZ_P"}, sch=(388.62, 363.22),
         desc="Buzzer current limit: 110 mA peak, 0.2 W at 50 % PWM, 0.41 W if stuck on (0.5 W part)"),
    dict(ref="D2", sym="SensorHAT:1N4148W_C81598", value="1N4148W",
         fp="SensorHAT:SOD-123F_L2.7-W1.6-LS3.8-RD",
         LCSC="C81598", MPN="1N4148W", Manufacturer="ST",
         pins={"1": "BUZ_P", "2": "BUZ_N"}, sch=(431.8, 378.46), desc="Buzzer flyback diode"),
    dict(ref="Q3", sym="SensorHAT:AO3400A", value="AO3400A",
         fp="SensorHAT:SOT-23_L2.9-W1.3-P1.90-LS2.4-BR",
         LCSC="C20917", MPN="AO3400A", Manufacturer="Alpha & Omega",
         pins={"1": "BUZ_G", "2": "GND", "3": "BUZ_N"}, sch=(454.66, 363.22), desc="Buzzer low-side switch"),
    R("R22", "100", "BUZ_PWM", "BUZ_G", "C22775", "0603WAF1000T5E", (434.34, 391.16), desc="Q3 gate series"),
    R("R23", "100k", "BUZ_G", "GND", "C25803", "0603WAF1003T5E", (452.12, 391.16), desc="Q3 gate pull-down (buzzer off at boot)"),


    # ---------------- XIAO host (ESP32-S3/C3/C6), never together with a Pi ----------------
    # J7 = XIAO D0..D6 (pin 1 at the USB-C end), J8 = 5V, GND, 3V3, D10, D9, D8, D7.
    # Boot straps: C3 GPIO2/8/9 are pulled high (R31/R26/R27); S3 GPIO3 (D2) is pulled low by R4,
    # which is ignored unless EFUSE_STRAP_JTAG_SEL is burned; the C6 exposes no strap pins.
    dict(ref="J7", sym="SensorHAT:PM254-1-07-Z-8.5", value="XIAO D0-D6",
         fp="SensorHAT:HDR-TH_7P-P2.54-V-F", LCSC="C2897370", MPN="PM254-1-07-Z-8.5", Manufacturer="HCTL",
         hand=True, pins={str(i + 1): f"XD{i}" for i in range(7)}, sch=(452.12, 76.2),
         desc="XIAO socket, left row: D0..D6"),
    dict(ref="J8", sym="SensorHAT:PM254-1-07-Z-8.5", value="XIAO 5V-D7",
         fp="SensorHAT:HDR-TH_7P-P2.54-V-F", LCSC="C2897370", MPN="PM254-1-07-Z-8.5", Manufacturer="HCTL",
         hand=True, pins={"1": "+5V_XIAO", "2": "GND", "3": "+3V3_XIAO", "4": "XD10", "5": "XD9", "6": "XD8", "7": "XD7"},
         sch=(452.12, 127.0), desc="XIAO socket, right row: 5V, GND, 3V3, D10, D9, D8, D7"),
    *[R(f"R{33 + i}", "100", f"XD{i}", net, "C22775", "0603WAF1000T5E", (487.68, 50.8 + 15.24 * i),
        desc=f"XIAO D{i} series resistor (limits current if both hosts are ever fitted)")
      for i, net in enumerate(["I2S_LRCLK", "I2S_BCLK", "I2S_DIN", "BUZ_PWM", "BTN", "XD5_SEL", "UART_TX",
                               "UART_RX", "I2C_SDA", "I2C_SCL", "LED_DATA"])],
    dict(ref="JP6", sym="Jumper:SolderJumper_3_Bridged12", value="D5 = 1-Wire | radar OUT",
         fp="Jumper:SolderJumper-3_P1.3mm_Bridged12_RoundedPad1.0x1.5mm",
         pins={"1": "ONEWIRE", "2": "XD5_SEL", "3": "GPIO17"}, sch=(515.62, 116.84), no_bom=True,
         desc="XIAO D5: 1-Wire (default, 1-2) or radar presence OUT (cut 1-2, bridge 2-3)"),
    R("R26", "4.7k", "+3V3", "I2C_SDA", "C23162", "0603WAF4701T5E", (530.86, 60.96),
      desc="I2C pull-up for XIAO mode; also holds the C3 GPIO8 strap high"),
    R("R27", "4.7k", "+3V3", "I2C_SCL", "C23162", "0603WAF4701T5E", (543.56, 60.96),
      desc="I2C pull-up for XIAO mode; also holds the C3 GPIO9 (BOOT) strap high"),
    R("R31", "10k", "+3V3", "I2S_LRCLK", "C25804", "0603WAF1002T5E", (556.26, 60.96),
      desc="Pull-up on the C3 GPIO2 strap (Espressif recommendation)"),

    # ---------------- Test points + mounting ----------------
    *[dict(ref=f"TP{i}", sym="Connector:TestPoint", value=net, fp="TestPoint:TestPoint_Pad_D1.5mm",
           pins={"1": net}, sch=(38.1 + 17.78 * i, 264.16), no_bom=True)
      for i, net in enumerate(["+5V", "+3V3", "+3V3_CO2", "GND", "EE_WP", "I2C_SDA", "I2C_SCL"], start=1)],
    *[dict(ref=f"MH{i}", sym="Mechanical:MountingHole", value="M2.5", fp="MountingHole:MountingHole_2.7mm_M2.5",
           pins={}, sch=(208.28 + 12.7 * i, 264.16), no_bom=True)
      for i in range(1, 5)],
]

SCH_TEXTS = [
    ("Sensor HAT v3 Universal - HAT for Raspberry Pi or Seeed XIAO host | SCD41 CO2 | SHT40 T/RH | SGP41 VOC/NOx | VEML7700 light | ICS-43434 mic",
     25.4, 20.32, 2.0),
    ("Raspberry Pi header (female socket, bottom side)", 25.4, 68.58, 1.6),
    ("Power: Pi 5 V or XIAO USB 5 V via ideal diodes -> +5V -> AP2112K-3.3 LDOs, enabled by Pi 3V3 OR XIAO 3V3", 101.6, 43.18, 1.6),
    ("I2C sensors: VEML7700 0x10, SHT40 0x44, SGP41 0x59, SCD41 0x62 (4.7k pull-ups; the Pi adds 1.8k)", 228.6, 43.18, 1.6),
    ("I2S microphone: GPIO18 BCLK, GPIO19 LRCLK, GPIO20 DIN / XIAO D1, D0, D2", 302.26, 104.14, 1.6),
    ("XIAO socket J7/J8 with 100R series resistors. NEVER fit a XIAO while the board sits on a Pi", 431.8, 43.18, 1.6),
    ("ID EEPROM (Pi 3V3; WP high = protected, bridge JP2 to program)", 25.4, 170.18, 1.6),
    ("1-Wire (GPIO4 / XIAO D5 via JP6)", 154.94, 170.18, 1.6),
    ("UART (GPIO14/15 / XIAO D6/D7) + GPIO17: series R, ESD, J3 pin 1 = 3.3 V (JP1) or switched/fused 5 V (JP3), never both", 228.6, 167.64, 1.6),
    ("Test points and mounting holes", 25.4, 254.0, 1.6),
    ("Particulate-matter port: own LDO, JP4 (closed) = 3.3 V for SEN6x, or cut JP4 + bridge JP5 = 5 V for SEN5x",
     25.4, 297.18, 1.6),
    ("5 V ideal-diode OR (LM66100 x2)", 170.18, 297.18, 1.6),
    ("VOC/NOx SGP41 (0x59)", 320.04, 297.18, 1.6),
    ("Expansion: Qwiic (3.3 V I2C) + GPIO pads (Pi only)", 393.7, 297.18, 1.6),
    ("Button GPIO27 / XIAO D4", 482.6, 297.18, 1.6),
    ("Status LED (GPIO10 / XIAO D10, 5 V via 74LV1T125) and buzzer (GPIO13 / XIAO D3, PWM)", 228.6, 355.6, 1.6),
]
