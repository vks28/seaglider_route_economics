"""
Seaglider Coastal Route Economics - Python engine
Boston (Long Wharf) <-> Nantucket, REGENT Viceroy Seaglider

Mirrors the logic of Seaglider_Route_PnL_Model.xlsx so results can be
cross-checked, and runs scenario + sensitivity analysis.

Usage:
    python seaglider_model.py            # prints scenario summary + sensitivity
"""

from copy import deepcopy

YEARS = 10
START_YEAR = 2028

# ---------------------------------------------------------------------------
# Assumptions (Base / Upside / Downside)
# ---------------------------------------------------------------------------
SCENARIOS = {
    "Base": dict(
        distance_mi=100, cruise_mph=180, harbor_hrs_per_leg=0.20, seats=12,
        fare_y1=199, fare_esc=0.03, ancillary_pct=0.05,
        lf_steady=0.70, op_days=290, legs_per_day=10,
        kwh_per_mi=3.0, power_cost=0.25,
        maint_per_bh=250, battery_cost=500_000, battery_cycles=3000,
        crew_sets=2.0, captain_salary=130_000, fo_salary=75_000, benefits_pct=0.30,
        insurance_pct=0.03, dock_fee=150, pax_fee=5, distribution_pct=0.04,
        ground_ops=1_500_000, ga_fixed=2_000_000, marketing_pct=0.03,
        craft_price=10_000_000, craft_life=15, residual_pct=0.10,
        terminals=2, infra_per_terminal=3_000_000, infra_life=10,
        cost_esc=0.03, tax_rate=0.25, discount_rate=0.10,
    ),
}
SCENARIOS["Upside"] = {**SCENARIOS["Base"], **dict(
    fare_y1=229, lf_steady=0.80, op_days=310, legs_per_day=11,
    kwh_per_mi=2.7, maint_per_bh=200, battery_cycles=3500, craft_price=9_000_000)}
SCENARIOS["Downside"] = {**SCENARIOS["Base"], **dict(
    fare_y1=169, lf_steady=0.55, op_days=260, legs_per_day=8,
    kwh_per_mi=3.5, maint_per_bh=325, battery_cycles=2000, craft_price=11_000_000)}

FLEET = [3, 5, 6, 6, 6, 6, 6, 6, 6, 6]
LF_RAMP = [0.80, 0.90, 1, 1, 1, 1, 1, 1, 1, 1]


def run(a, fleet=FLEET, ramp=LF_RAMP):
    bh_leg = a["distance_mi"] / a["cruise_mph"] + a["harbor_hrs_per_leg"]
    rows = []
    cum = 0.0
    cum_capex = 0.0
    cum_da = 0.0
    prev_fleet = 0
    for i in range(YEARS):
        y = i + 1
        esc = (1 + a["cost_esc"]) ** (y - 1)
        f = fleet[i]
        lf = min(0.95, a["lf_steady"] * ramp[i])
        legs = f * a["legs_per_day"] * a["op_days"]
        bh = legs * bh_leg
        seats_av = legs * a["seats"]
        pax = seats_av * lf
        asm = seats_av * a["distance_mi"]
        fare = a["fare_y1"] * (1 + a["fare_esc"]) ** (y - 1)
        ticket = pax * fare
        anc = ticket * a["ancillary_pct"]
        rev = ticket + anc

        energy = legs * a["distance_mi"] * a["kwh_per_mi"] * a["power_cost"] * esc
        crew = f * a["crew_sets"] * (a["captain_salary"] + a["fo_salary"]) * (1 + a["benefits_pct"]) * esc
        maint = bh * a["maint_per_bh"] * esc
        battery = legs * a["battery_cost"] / a["battery_cycles"]
        insurance = f * a["craft_price"] * a["insurance_pct"]
        dock = (legs * a["dock_fee"] + pax * a["pax_fee"]) * esc
        dist = rev * a["distribution_pct"]
        ground = a["ground_ops"] * esc
        ga = a["ga_fixed"] * esc + rev * a["marketing_pct"]
        opex = energy + crew + maint + battery + insurance + dock + dist + ground + ga
        ebitda = rev - opex

        dep_fleet = f * a["craft_price"] * (1 - a["residual_pct"]) / a["craft_life"]
        infra_total = a["terminals"] * a["infra_per_terminal"]
        dep_infra = infra_total / a["infra_life"] if y <= a["infra_life"] else 0
        da = dep_fleet + dep_infra
        ebit = ebitda - da
        tax = max(0.0, ebit) * a["tax_rate"]
        ni = ebit - tax

        capex = (f - prev_fleet) * a["craft_price"] + (infra_total if y == 1 else 0)
        fcf = ni + da - capex
        cum_capex += capex
        cum_da += da
        residual = (cum_capex - cum_da) if y == YEARS else 0
        fcf_total = fcf + residual
        cum += fcf

        # breakeven load factors
        unit = seats_av * (fare * (1 + a["ancillary_pct"]) * (1 - a["distribution_pct"] - a["marketing_pct"])
                           - a["pax_fee"] * esc)
        pax_var = rev * (a["distribution_pct"] + a["marketing_pct"]) + pax * a["pax_fee"] * esc
        fixedish = opex - pax_var
        belf_ebit = (fixedish + da) / unit
        belf_cash = fixedish / unit

        rows.append(dict(
            year=START_YEAR + i, fleet=f, lf=lf, legs=legs, pax=pax, asm=asm, fare=fare,
            revenue=rev, energy=energy, crew=crew, maint=maint, battery=battery,
            insurance=insurance, dock=dock, distribution=dist, ground=ground, ga=ga,
            opex=opex, ebitda=ebitda, da=da, ebit=ebit, ni=ni, capex=capex, fcf=fcf,
            fcf_total=fcf_total, cum_fcf=cum,
            casm_c=(opex + da) / asm * 100, rasm_c=rev / asm * 100,
            belf_ebit=belf_ebit, belf_cash=belf_cash,
        ))
        prev_fleet = f
    return rows


def npv(rate, flows):
    return sum(cf / (1 + rate) ** (t + 1) for t, cf in enumerate(flows))


def irr(flows, lo=-0.99, hi=1.0):
    f = lambda r: sum(cf / (1 + r) ** t for t, cf in enumerate(flows))  # Excel IRR convention
    if f(lo) * f(hi) > 0:
        return None
    for _ in range(200):
        mid = (lo + hi) / 2
        if f(lo) * f(mid) <= 0:
            hi = mid
        else:
            lo = mid
    return mid


def summarize(a):
    rows = run(a)
    flows = [r["fcf_total"] for r in rows]
    negatives = sum(1 for r in rows if r["cum_fcf"] < 0)
    payback = None if negatives >= YEARS else negatives + 1
    y3 = rows[2]
    return dict(
        npv=npv(a["discount_rate"], flows), irr=irr(flows), payback_year=payback,
        y3_revenue=y3["revenue"], y3_ebitda=y3["ebitda"], y3_ebitda_margin=y3["ebitda"] / y3["revenue"],
        y3_ebit=y3["ebit"], y3_casm=y3["casm_c"], y3_rasm=y3["rasm_c"],
        y3_belf=y3["belf_ebit"], y3_belf_cash=y3["belf_cash"], y3_pax=y3["pax"],
        cum_fcf_10=rows[-1]["cum_fcf"],
    )


# Sensitivity: flex one driver at a time around Base
SENSITIVITY_DRIVERS = [
    ("Average fare (Y1)", "fare_y1", 0.20),
    ("Load factor (steady state)", "lf_steady", 0.20),
    ("Legs per craft per day", "legs_per_day", 0.20),
    ("Operating days per year", "op_days", 0.10),
    ("Craft purchase price", "craft_price", 0.20),
    ("Battery cycle life", "battery_cycles", 0.30),
    ("Maintenance $ / block hour", "maint_per_bh", 0.30),
    ("Energy use (kWh / mile)", "kwh_per_mi", 0.20),
]


def sensitivity(base=None):
    base = base or SCENARIOS["Base"]
    base_npv = summarize(base)["npv"]
    out = []
    for label, key, pct in SENSITIVITY_DRIVERS:
        lo, hi = deepcopy(base), deepcopy(base)
        lo[key] = base[key] * (1 - pct)
        hi[key] = base[key] * (1 + pct)
        out.append(dict(driver=label, flex=pct, low_value=lo[key], high_value=hi[key],
                        npv_low=summarize(lo)["npv"], npv_high=summarize(hi)["npv"],
                        base_npv=base_npv))
    out.sort(key=lambda d: abs(d["npv_high"] - d["npv_low"]), reverse=True)
    return out


def lf_fare_grid(base=None, lfs=(0.50, 0.60, 0.70, 0.80, 0.90), fares=(149, 174, 199, 224, 249)):
    base = base or SCENARIOS["Base"]
    grid = []
    for lf in lfs:
        row = []
        for fare in fares:
            a = {**base, "lf_steady": lf, "fare_y1": fare}
            row.append(summarize(a)["npv"])
        grid.append(row)
    return lfs, fares, grid


if __name__ == "__main__":
    for name, a in SCENARIOS.items():
        s = summarize(a)
        irr_txt = f"{s['irr']:.1%}" if s["irr"] is not None else "n/a"
        print(f"{name:9s} NPV ${s['npv']/1e6:7.1f}M  IRR {irr_txt:>6s}  payback yr {s['payback_year']}  "
              f"Y3 rev ${s['y3_revenue']/1e6:5.1f}M  EBITDA {s['y3_ebitda_margin']:.0%}  "
              f"CASM {s['y3_casm']:.1f}c  BELF {s['y3_belf']:.0%}  pax {s['y3_pax']:,.0f}")
    print("\nTornado (NPV, $M):")
    for d in sensitivity():
        print(f"  {d['driver']:30s} {d['npv_low']/1e6:7.1f} .. {d['npv_high']/1e6:7.1f}")
