# Polling Proposal

Pitch materials for **Augur**’s polling / forecasting work on the **2026 Hungarian parliamentary election** (12 April 2026).

## What’s in the repo (minimal set)

| Item | Role |
|------|------|
| `build_headline_workbook.py` | Builds `headline_pitch_data.xlsx`: **official party-list** true result, **likely-voter** internal row (from the source xlsx), and **three** public polls (21 Kutatóközpont, Medián, Alapjogokért Központ) per the English **Wikipedia** 2026 polling table. |
| `Headline Predictions (1).xlsx` | Source for the **Augur likely-voter** scenario only (one internal model run). **Required** to rebuild. |
| `headline_pitch_data.xlsx` | **Output** of the build — used by the plot script. |
| `plot_pitch_deck.py` | Writes the two PNGs in `plots/`. |
| `requirements.txt` | `pandas`, `matplotlib`, `openpyxl` |

**Important:** the **true result** row uses **national party list** percentages (Wikipedia / NVI list vote), **not** constituency (SMD) vote shares.

## Rebuild data and figures

```bash
python3 -m pip install -r requirements.txt
python3 build_headline_workbook.py
MPLCONFIGDIR=/tmp/mpl python3 plot_pitch_deck.py
```

## Outputs

- `plots/2026_hungary_list_vote_pitch.png` — list vote comparison  
- `plots/2026_hungary_list_vote_error_pitch.png` — error vs. official list result (pp)  

## Disclaimer

Public numbers are as transcribed from Wikipedia; before external use, confirm against each pollster’s published tables.
