# SPDX-FileCopyrightText: 2026 Emanuel Bachmann
# SPDX-License-Identifier: MIT
"""Erster Funktionstest fuer den Sensor HAT v3 auf dem Raspberry Pi (Pi-Modus, ohne XIAO).

Installation (im venv):
    pip install adafruit-blinka adafruit-circuitpython-scd4x adafruit-circuitpython-sht4x \
        adafruit-circuitpython-veml7700 adafruit-circuitpython-neopixel-spi w1thermsensor gpiozero
Aufruf:
    sudo ~/hat/bin/python3 sensor_test.py   (sudo fuer den Summer)
"""
import os
import time

import board
import busio

i2c = busio.I2C(board.SCL, board.SDA)

while not i2c.try_lock():
    pass
found = [hex(a) for a in i2c.scan()]
i2c.unlock()
print("I2C-Adressen:", found, "(erwartet: 0x10 VEML7700, 0x44 SHT40, 0x59 SGP41, 0x62 SCD41;"
      " mit Feinstaubsensor zusaetzlich 0x6B SEN6x oder 0x69 SEN5x)")

try:
    import adafruit_veml7700
    veml = adafruit_veml7700.VEML7700(i2c)
    print(f"VEML7700: {veml.lux:.1f} lx")
except Exception as e:  # noqa: BLE001 - Testskript, jeden Sensor einzeln melden
    print("VEML7700 Fehler:", e)

try:
    import adafruit_sht4x
    sht = adafruit_sht4x.SHT4x(i2c)
    t, rh = sht.measurements
    print(f"SHT40: {t:.2f} C, {rh:.1f} %rF")
except Exception as e:  # noqa: BLE001
    print("SHT40 Fehler:", e)


def crc8(data):
    """Sensirion CRC-8 (Polynom 0x31, Start 0xFF)."""
    crc = 0xFF
    for b in data:
        crc ^= b
        for _ in range(8):
            crc = ((crc << 1) ^ 0x31) & 0xFF if crc & 0x80 else (crc << 1) & 0xFF
    return crc


def sgp41_raw(command):
    """SGP41 Rohwerte: 0x2612 = Konditionierung (nur VOC), 0x2619 = VOC + NOx.
    Mit Standard-Kompensation 50 %rF / 25 C (0x8000 / 0x6666)."""
    args = [0x80, 0x00, crc8([0x80, 0x00]), 0x66, 0x66, crc8([0x66, 0x66])]
    while not i2c.try_lock():
        pass
    try:
        i2c.writeto(0x59, bytes([command >> 8, command & 0xFF] + args))
        time.sleep(0.06)
        buf = bytearray(6 if command == 0x2619 else 3)
        i2c.readfrom_into(0x59, buf)
    finally:
        i2c.unlock()
    words = []
    for i in range(0, len(buf), 3):
        if crc8(buf[i:i + 2]) != buf[i + 2]:
            raise ValueError("CRC-Fehler")
        words.append(buf[i] << 8 | buf[i + 1])
    return words


try:
    for _ in range(9):                       # ca. 9 s Konditionierung (Datenblatt: hoechstens 10 s)
        sgp41_raw(0x2612)
        time.sleep(1)
    voc, nox = sgp41_raw(0x2619)
    print(f"SGP41: Rohwert VOC {voc}, NOx {nox} (Index-Berechnung: pip install sensirion-gas-index-algorithm)")
except Exception as e:  # noqa: BLE001
    print("SGP41 Fehler:", e)

try:
    import adafruit_scd4x
    scd = adafruit_scd4x.SCD4X(i2c)
    print("SCD41 Seriennummer:", [hex(x) for x in scd.serial_number])
    scd.start_periodic_measurement()
    print("SCD41: warte auf erste Messung (ca. 5 s) ...")
    for _ in range(20):
        if scd.data_ready:
            print(f"SCD41: {scd.CO2} ppm CO2, {scd.temperature:.1f} C, {scd.relative_humidity:.0f} %rF")
            break
        time.sleep(1)
    scd.stop_periodic_measurement()
except Exception as e:  # noqa: BLE001
    print("SCD41 Fehler:", e)

try:
    from gpiozero import Button
    print("Taster GPIO27:", "gedrueckt" if Button(27, pull_up=None, active_state=False).is_pressed else "nicht gedrueckt")
except Exception as e:  # noqa: BLE001
    print("Taster Fehler:", e)

try:
    import neopixel_spi
    led = neopixel_spi.NeoPixel_SPI(board.SPI(), 1, pixel_order=neopixel_spi.GRB, auto_write=True)
    for color in ((40, 0, 0), (0, 40, 0), (0, 0, 40), (0, 0, 0)):
        led[0] = color
        time.sleep(0.4)
    print("Status-LED: rot, gruen, blau, aus")
except Exception as e:  # noqa: BLE001
    print("Status-LED Fehler (dtparam=spi=on gesetzt?):", e)

try:
    pwm = "/sys/class/pwm/pwmchip0"
    if not os.path.exists(pwm + "/pwm1"):
        open(pwm + "/export", "w").write("1")
        time.sleep(0.2)
    for name, value in (("period", "250000"), ("duty_cycle", "125000"), ("enable", "1")):
        open(f"{pwm}/pwm1/{name}", "w").write(value)
    time.sleep(0.2)
    open(pwm + "/pwm1/enable", "w").write("0")
    print("Summer: 0,2 s Ton mit 4 kHz")
except Exception as e:  # noqa: BLE001
    print("Summer Fehler (dtoverlay=pwm,pin=13,func=4 gesetzt? Skript mit sudo starten):", e)

try:
    from w1thermsensor import W1ThermSensor
    for s in W1ThermSensor.get_available_sensors():
        print(f"DS18B20 {s.id}: {s.get_temperature():.2f} C")
except Exception as e:  # noqa: BLE001
    print("1-Wire: kein Sensor oder Fehler:", e)
