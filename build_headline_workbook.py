#!/usr/bin/env python3
"""
Build `headline_pitch_data.xlsx` for the pitch deck.

- **True result:** national *party-list* vote shares (12 Apr 2026), not constituency
  splits (per Wikipedia election infobox / NVI party-list totals).
- **Internal:** Augur likely-voter run from `Headline Predictions (1).xlsx`.
- **Public (selected):** 21 Kutatóközpont (8–11 Apr 2026), Medián (7–11 Apr 2026),
  Alapjogokért Központ (28–29 Mar 2026, government-leaning) — figures per English
  Wikipedia 2026 polling table; verify before publication.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
OUT_XLSX = ROOT / "headline_pitch_data.xlsx"
SOURCE = ROOT / "Headline Predictions (1).xlsx"

PARTIES = ["Tisza", "Fidesz", "MH", "MKKP", "DK"]

# Official party-list % (Wikipedia: 2026 election results, party-list column;
# Tisza / Fidesz–KDNP / MH / DK / MKKP). Sum < 100 due to other lists — normalize to 1.
_OFFICIAL_LIST_PCT: dict[str, float] = {
    "Tisza": 53.18,
    "Fidesz": 38.61,
    "MH": 5.63,
    "DK": 1.10,
    "MKKP": 0.82,
}

# (label, fidesz, tisza, mh, dk, mkkp, others_or_None) — % among headline party columns
# Order matches Wikipedia 2026 table: Fidesz, Tisza, MH, DK, MKKP, [Others]
PUBLIC_POLLS: list[tuple] = [
    # en.wikipedia: 2026 election period table (late campaign). Label must not start
    # with digits or Excel may mangle the cell when opening the xlsx.
    (
        "Kutatóközpont (21 Research) (8–11 Apr 2026)",
        38.0,
        55.0,
        5.0,
        1.0,
        1.0,
        None,
    ),
    (
        "Medián (7–11 Apr 2026)",
        37.9,
        55.5,
        3.9,
        1.4,
        1.3,
        None,
    ),
    (
        "Alapjogokért Központ (28–29 Mar 2026)",
        50.0,
        42.0,
        5.0,
        2.0,
        1.0,
        None,
    ),
]

INTERNAL_VERSION = "Apr12 final Data, 80% TO, VLikely Voters"


def _normalize_party_shares(pct: dict[str, float]) -> dict[str, float]:
    s = sum(pct[p] for p in PARTIES)
    if s <= 0:
        raise ValueError("Invalid official percentages")
    return {p: pct[p] / s for p in PARTIES}


def _official_to_long() -> list[dict]:
    norm = _normalize_party_shares(_OFFICIAL_LIST_PCT)
    return [
        {
            "Version": "True Election Result",
            "Party": p,
            "Pct": norm[p],
            "Source": "Party-list result (12 Apr 2026), per Wikipedia / NVI",
        }
        for p in PARTIES
    ]


def _to_long(
    version: str,
    f: float,
    t: float,
    mh: float,
    dk: float,
    mkk: float,
    others: float | None,
) -> list[dict]:
    f, t, mh, dk, mkk = f / 100, t / 100, mh / 100, dk / 100, mkk / 100
    if others is not None and (not np.isnan(others)) and float(others) > 0:
        o = float(others) / 100.0
        mh += o * 0.25
        dk += o * 0.40
        mkk += o * 0.35
    s = t + f + mh + dk + mkk
    if s > 0 and abs(s - 1.0) > 0.001:
        t, f, mh, dk, mkk = t / s, f / s, mh / s, dk / s, mkk / s
    m = {
        "Tisza": t,
        "Fidesz": f,
        "MH": mh,
        "MKKP": mkk,
        "DK": dk,
    }
    return [
        {
            "Version": version,
            "Party": p,
            "Pct": m[p],
            "Source": "Wikipedia 2026 polling table",
        }
        for p in PARTIES
    ]


def _load_augur_likely() -> list[dict]:
    raw = pd.read_excel(SOURCE)
    raw["Version"] = (
        raw["Version"].astype(str).str.strip().str.replace(r"^\d+\s*", "", regex=True)
    )
    part = raw[raw["Version"] == INTERNAL_VERSION]
    rows: list[dict] = []
    for _, r in part.iterrows():
        if pd.isna(r.get("Pct")):
            continue
        rows.append(
            {
                "Version": INTERNAL_VERSION,
                "Party": r["Party"],
                "Pct": float(r["Pct"]),
                "Source": "Augur internal (likely-voter scenario, 12 Apr 2026 run)",
            }
        )
    if not rows:
        raise SystemExit(
            f"No rows for '{INTERNAL_VERSION}' in {SOURCE}. Restore the xlsx or update INTERNAL_VERSION."
        )
    return rows


def build() -> None:
    parts: list[list[dict]] = []
    parts.append(_official_to_long())
    parts.append(_load_augur_likely())
    for label, a, b, c, d, e, o in PUBLIC_POLLS:
        parts.append(_to_long(label, a, b, c, d, e, o))
    out = pd.DataFrame(
        [row for block in parts for row in block],
    )
    for col in ("Direct Mandates", "List Mandates", "Total Mandates"):
        out[col] = np.nan
    out.to_excel(OUT_XLSX, index=False)
    n_v = out["Version"].nunique()
    print(f"Wrote {OUT_XLSX}  ({len(out)} rows, {n_v} versions).")


if __name__ == "__main__":
    build()
