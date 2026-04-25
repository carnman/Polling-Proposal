# Polling Proposal

Materials for **Augur Technologies**’ polling / forecasting pitch: national **party list** vote shares for the **2026 Hungarian parliamentary election** (12 April 2026), with emphasis on the internal **likely-voter** model run (12 Apr 2026) versus a small set of public benchmarks.

## What is in this repo

- **`Headline Predictions (1).xlsx`** — original internal extracts (true list result + model scenarios, plus seat columns in some rows).
- **`build_headline_workbook.py`** — builds **`Headline_Predictions_Combined_2026.xlsx`**: transfers Augur runs and the official result, and appends a curated set of public polls (many from the English Wikipedia *Opinion polling for the 2026 Hungarian parliamentary election* table) plus an **Atlas Intel** row (5–10 Apr 2026 fieldwork; headline numbers per AtlasIntel.org / common aggregations).
- **`plot_pitch_deck.py`** — generates the **pitch-deck** figures in **`plots/`** (large type, high contrast, few comparators: official result, **Augur likely-voter** scenario, Atlas Intel, Publicus, McLaughlin).
- **`party_sahres (2).ipynb`** — exploratory notebook (constituency work is out of scope for the pitch figures).

## Regenerate the pitch figures

```bash
python3 -m pip install -r requirements.txt
python3 build_headline_workbook.py
python3 plot_pitch_deck.py
```

Optional: `PITCH_DATA=path/to/sheet.xlsx python3 plot_pitch_deck.py`

## Output charts

| File | Content |
|------|---------|
| `plots/2026_hungary_list_vote_pitch.png` | National **list** vote (headline shares) |
| `plots/2026_hungary_list_vote_error_pitch.png` | Error in pp vs. official list result |

These are **not** seat projections. Small-party buckets follow the same five party columns as the internal sheet.

## Disclaimer

Public poll numbers are compiled for illustration; always cite original pollsters. Wikipedia tables can contain transcription errors—verify before external publication.
