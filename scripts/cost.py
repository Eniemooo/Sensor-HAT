# SPDX-FileCopyrightText: 2026 Emanuel Bachmann
# SPDX-License-Identifier: MIT
"""Estimate the landed cost per board for a JLCPCB order of N boards (group-buy planning).

Part prices and stock come live from the JLCPCB parts API. Fees, PCB, shipping and VAT
are ESTIMATES (JLCPCB price list of 2026-10-22, see README); the JLCPCB quote is binding.
Usage: python3 -I cost.py [quantities ...]     e.g.  python3 -I cost.py 2 5 20 50 100
"""
import json
import math
import os
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import design  # noqa: E402

API = "https://jlcpcb.com/api/overseas-pcb-order/v1/shoppingCart/smtGood/selectSmtComponentList"
EUR_PER_USD = 0.89
VAT = 0.19
SETUP, STENCIL, FEEDER = 25.56, 8.21, 1.53            # Standard PCBA, single side
XRAY = [(10, 1.64), (50, 0.82), (200, 0.49), (10 ** 9, 0.33)]   # USD per X-rayed part, by count
LEADLESS = {"U1", "U3", "U13", "U2"}                   # SCD41, ICS-43434, SGP41, SHT40 -> X-ray
THT_ORDER, THT_JOINT = 3.58, 0.0164                     # JLC hand soldering of J2/J3/J7/J8 (J1 always by hand)
THT_JOINTS = 3 + 5 + 7 + 7
# 4-layer 65x56 mm (75x70 with rails), 1.6 mm, ENIG: rough price per quantity (USD, ESTIMATE -
# check the JLCPCB quote; the 2-layer ENIG price for 5 pcs was 21.20 USD on 2026-10-22)
PCB_ENIG = [(5, 32.0), (10, 40.0), (20, 55.0), (30, 65.0), (50, 85.0), (100, 130.0), (250, 280.0)]


def part_info(lcsc):
    req = urllib.request.Request(API, data=json.dumps({"keyword": lcsc, "currentPage": 1, "pageSize": 5}).encode(),
                                 headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    for c in data.get("data", {}).get("componentPageInfo", {}).get("list", []) or []:
        if c.get("componentCode") == lcsc:
            return c
    return None


def unit_price(info, qty):
    best = None
    for tier in info.get("componentPrices") or []:
        if qty >= tier["startNumber"]:
            best = tier["productPrice"]
    return best if best is not None else (info.get("componentPrices") or [{"productPrice": 0}])[0]["productPrice"]


def tier(table, n):
    for limit, value in table:
        if n <= limit:
            return value
    return table[-1][1]


def main(quantities):
    lines = {}
    for p in design.PARTS:
        if p["ref"].startswith("#") or p.get("no_bom") or not p.get("LCSC"):
            continue
        ln = lines.setdefault(p["LCSC"], {"refs": [], "hand": bool(p.get("hand")), "value": p["value"]})
        ln["refs"].append(p["ref"])
    infos = {}
    for lcsc in lines:
        try:
            infos[lcsc] = part_info(lcsc)
        except Exception as e:  # noqa: BLE001
            print("API error", lcsc, e)
            infos[lcsc] = None
    smd = {k: v for k, v in lines.items() if not v["hand"]}
    print(f"{len(smd)} SMD BOM lines, {len(lines) - len(smd)} THT lines (hand / JLC THT)")
    low = [(k, v["value"], infos[k]["stockCount"], infos[k]["componentLibraryType"])
           for k, v in lines.items() if infos[k]]
    for k, val, stock, lib in sorted(low, key=lambda x: x[2])[:8]:
        print(f"  lowest stock: {k:10} {val:28} {stock:>8}  {lib}")
    print()
    print(f"{'boards':>6} {'parts/board':>11} {'fees/board':>10} {'PCB/board':>9} {'ship+VAT/board':>14} "
          f"{'EUR/board SMD':>13} {'EUR/board all':>13} {'order EUR':>10}")
    for n in quantities:
        parts = 0.0
        tht = 0.0
        for lcsc, ln in lines.items():
            info = infos[lcsc]
            if not info:
                continue
            per_board = len(ln["refs"])
            need = per_board * n
            if not ln["hand"] and ln["refs"][0][0] in "RC":
                need += max(5, math.ceil(0.05 * need))        # attrition for passives (estimate)
            least = info.get("leastNumber") or info.get("minPurchaseNum") or 0
            need = max(need, least or 0)
            cost = need * unit_price(info, need)
            if ln["hand"]:
                tht += cost
            else:
                parts += cost
        xray_parts = len(LEADLESS) * n
        fees = SETUP + STENCIL + FEEDER * len(smd) + xray_parts * tier(XRAY, xray_parts) + 0.5
        tht_fees = THT_ORDER + THT_JOINT * THT_JOINTS * n
        pcb = tier(PCB_ENIG, max(n, 5))
        weight = 0.1 + 0.012 * max(n, 5)
        ship = 23.5 + max(0.0, weight - 0.3) * 9.0
        smd_total = (parts + fees + pcb + ship) * (1 + VAT)
        all_total = smd_total + (tht + tht_fees) * (1 + VAT)
        print(f"{n:>6} {parts / n:>11.2f} {fees / n:>10.2f} {pcb / n:>9.2f} {(ship + (parts + fees + pcb + ship) * VAT) / n:>14.2f} "
              f"{smd_total * EUR_PER_USD / n:>13.2f} {all_total * EUR_PER_USD / n:>13.2f} {all_total * EUR_PER_USD:>10.0f}")
    print("\nUSD columns are per board; EUR incl. 19% VAT and DHL DDP. 'SMD' = headers soldered by hand,")
    print("'all' = JLC also solders J2, J3 and the XIAO sockets (J1 stays a hand job). The header parts themselves")
    print("are only counted in the 'all' column.")
    print("All fees and PCB/shipping are estimates.")


if __name__ == "__main__":
    main([int(q) for q in sys.argv[1:]] or [2, 5, 10, 20, 50, 100])
