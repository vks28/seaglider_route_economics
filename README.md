# Seaglider Coastal Route Economics: Boston – Nantucket

A business case and 10-year P&L model for launching an electric **REGENT Viceroy Seaglider** service between Boston and Nantucket. The project tests whether a 6-craft fleet can earn its cost of capital, and which commercial and operating levers matter most.

## Key findings (Base case)

| Metric | Result |
|---|---|
| 10-year NPV (10% hurdle) | **-$0.8M** (roughly breakeven) |
| 10-year IRR | **9.7%** |
| Payback year | **2036** |
| Total capex | $66M (fleet + docks and charging) |
| 2030 revenue / EBITDA margin | $32.4M / 31% |
| CASM vs. RASM (2030) | 128¢ vs. 155¢ |
| Breakeven load factor | **56%** vs. 70% assumed |

**Takeaways**
- The route is **viable but not yet compelling** on Base assumptions. It returns about the cost of capital.
- **Fare and load factor dominate.** A ±20% change in either swings NPV by about $25–28M, which is more than any cost driver.
- **Operating leverage is high.** Most costs are per leg or fixed, so an extra passenger on a scheduled leg is mostly margin.
- **Energy is about 6% of operating cost.** Utilization (legs per day, operating days) matters far more than electricity price.

| Scenario | NPV | IRR | Payback |
|---|---|---|---|
| Upside | +$72.6M | 41.5% | 2032 |
| Base | -$0.8M | 9.7% | 2036 |
| Downside | -$80.4M | n/a | Beyond 2037 |

## Repository contents

| File | Description |
|---|---|
| `Seaglider_Route_PnL_Model.xlsx` | Driver-based Excel model with live formulas: Summary, Assumptions (with scenario selector), 10-year Model (operations, P&L, cash flow, unit economics), Sensitivity, Sources |
| `Seaglider_Route_Business_Case.pptx` | 8-slide executive deck with native charts and speaker notes |
| `seaglider_model.py` | Python version of the model: scenario comparison, tornado sensitivity, and an NPV grid by load factor and fare |

## Model structure

```
Assumptions (Base / Upside / Downside)
        │
        ▼
Operations: fleet × legs/day × operating days → legs flown
            legs × seats × load factor       → passengers
        │
        ▼
Revenue:    passengers × fare (+ ancillary)
Costs:      energy, crew, maintenance, battery reserve, insurance,
            dock & passenger fees, distribution, ground ops, G&A & marketing
        │
        ▼
P&L → EBITDA → D&A → EBIT → tax → net income
Cash flow → capex → free cash flow → NPV, IRR, payback
Unit economics → CASM, RASM, cost per passenger, breakeven load factor
```

**Using the Excel model:** On the `Assumptions` sheet, set cell **B3** to 1 (Base), 2 (Upside) or 3 (Downside). You can also edit any blue input. Every other sheet recalculates.
Color convention: blue = input, black = formula, green = link to another sheet.

## Running the Python model

Requires Python 3.8+ and the standard library only.

```bash
python seaglider_model.py
```

The script prints the NPV, IRR, payback, revenue, EBITDA margin, CASM and breakeven load factor for each scenario, followed by a tornado sensitivity ranking. Its outputs match the Excel model exactly.

## Key assumptions

- **Route:** 100 statute miles one way, 180 mph cruise plus about 12 min of harbor and hydrofoil time per leg (about 45 min dock-to-dock).
- **Craft:** 12 passengers and 2 crew (REGENT specification).
- **Fleet:** ramps from 3 to 5 to 6 craft over 2028–2030. Service launches in 2028, after REGENT's targeted first deliveries in late 2027.
- **Pricing:** $199 average one-way fare. This sits below Boston–Nantucket flights ($190–367) and above bus plus ferry ($55–85, about 4 hours).
- **Demand:** 70% steady-state load factor, ramping up over the first two years.
- **Analyst estimates:** craft price ($10M), maintenance, battery cycle life, energy use and overhead are estimates, because REGENT has not published them. Each one is a separate input that can be changed.

## Sources

- [REGENT – Viceroy Seaglider](https://www.regentcraft.com/seagliders/viceroy)
- [REGENT – Viceroy specifications FAQ](https://www.regentcraft.com/news/regent-seaglider-specifications)
- [ch-aviation – initial East Coast routes incl. Boston–Nantucket](https://www.ch-aviation.com/news/162847)
- [Smart Cities Dive – first deliveries targeted late 2027](https://www.smartcitiesdive.com/news/regent-seaglider-takes-flight-first-public-demo/831857/)
- [Rome2rio – Boston–Nantucket distance and travel options](https://www.rome2rio.com/s/Boston/Nantucket)

## Disclaimer

This is an independent, illustrative analysis built from public information and stated assumptions. It is not affiliated with or endorsed by REGENT Craft Inc.

---
**Author:** Khushi Saraswat Vikash · MS Business Analytics, University of Illinois Chicago
