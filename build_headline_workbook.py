#!/usr/bin/env python3
"""
Assemble a new headline-predictions workbook: Augur (internal) + election result
+ curated public pollsters. Numbers in WIKI_POLLS are taken from the English
Wikipedia table “Opinion polling for the 2026 Hungarian parliamentary election”
(2024–26 section; fieldwork order Fidesz, Tisza, MH, DK, MKKP, Others, Lead),
interpreted in row order. Cross-check a few rows if you republish.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
OUT_XLSX = ROOT / "Headline_Predictions_Combined_2026.xlsx"
SOURCE = ROOT / "Headline Predictions (1).xlsx"
PARTIES = ["Tisza", "Fidesz", "MH", "MKKP", "DK"]

# --- Curated 2024–26 polls: (label, fidesz, tisza, mi_hazank, dk, mkkp, others_or_None)
# Percentages; None or NaN in others means column absent / en-dash. If numeric, it is
# the “Other” bucket from Wikipedia: we reallocate 2/3 to MKKP+DK / 1/3 to MH in tiny amounts
# (see _to_long) so the five main parties stay in one framework.
# Extra pollster not on wiki page: PolitPro/Atlas style headline, clearly marked.
WIKI_POLLS: list[tuple] = [
    # Late campaign / 2026 (Wikipedia 2026 election period table, reverse chrono in article)
    ("Publicus (7–9 Apr 2026)", 39, 52, 2, 5, 2, None),
    ("McLaughlin & Associates (7 Apr 2026)", 45.4, 39.7, 4.6, 7.5, 2.2, 0.6),
    ("Iránytű Institute (31 Mar–4 Apr 2026)", 40, 51, 1, 4, 4, 0.0),
    ("IDEA (29 Mar–4 Apr 2026)", 37, 50, 4, 5, 2, 2.0),
    ("Publicus (27–30 Mar 2026)", 40, 49, 3, 6, 3, None),
    ("Alapjogokért Központ (28–29 Mar 2026)", 50, 42, 2, 5, 1, None),
    ("Závecz Research (24–28 Mar 2026)", 38, 51, 3, 5, 3, None),
    (
        "21 Kutatóközpont (23–28 Mar 2026) — enwiki",
        37,
        56,
        1,
        5,
        1,
        None,
    ),
    ("XXI. Század (26–27 Mar 2026)", 46, 41, 5, 6, 2, None),
    ("Republikon (23–26 Mar 2026)", 40, 49, 2, 5, 4, None),
    ("Nézőpont (23–24 Mar 2026)", 46, 40, 3, 8, 3, None),
    ("Medián (17–20 Mar 2026) — enwiki", 35, 58, 1, 4, 2, None),
    ("Minerva (10–11 Mar 2026) — enwiki", 40.1, 51.3, 1.4, 5.5, 1.7, None),
    ("7–9 Mar 2026 XXI. Század", 46, 41, 4, 6, 3, None),
    ("21 Kutatóközpont (2–6 Mar 2026)", 39, 53, 2, 5, 1, None),
    ("IDEA (28 Feb–6 Mar 2026)", 37, 49, 5, 6, 2, 1.0),
    ("Závecz Research (22–28 Feb 2026)", 38, 50, 3, 7, 2, None),
    ("Minerva (20–25 Feb 2026) — enwiki", 41.5, 50.0, 2.8, 4.1, 1.7, None),
    ("Nézőpont (20–25 Feb 2026)", 45, 40, 3, 8, 4, None),
    ("Publicus (24–28 Feb 2026)", 39, 47, 4, 6, 4, None),
    ("Medián (18–23 Feb 2026) — enwiki", 35, 55, 2, 6, 2, None),
    ("Nézőpont (9–11 Feb 2026)", 46, 40, 4, 7, 3, 0.0),
    ("Alapjogokért Központ (2–5 Feb 2026)", 49, 42, 2, 5, 2, 0.0),
    ("IDEA (31 Jan–6 Feb 2026)", 38, 48, 5, 5, 3, 1.0),
    ("IDEA (31 Dec 2025–6 Jan 2026) — enwiki", 38, 48, 5, 4, 3, 0.0),
    ("Publicus (16–20 Dec 2025) — enwiki", 40, 48, 5, 5, 3, None),
    ("Nézőpont (5–7 Jan 2026)", 47, 40, 3, 6, 4, 0.0),
    # Atlas Intel — national list poll (fieldwork 5–10 Apr 2026, n=1,587). Headline
    # shares as reported by AtlasIntel.org and secondary aggregators; not all rows
    # appear in the en.wikipedia 2026 table, but the figure matches PolitPro’s summary.
    (
        "Atlas Intel (10 Apr 2026) — reported aggregate",
        39.3,
        52.1,
        5.1,
        1.5,
        1.4,
        0.6,
    ),
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
    return [{"Version": version, "Party": p, "Pct": m[p], "Source": "Wikipedia / public"} for p in PARTIES]


def load_internal_augur_and_true() -> pd.DataFrame:
    raw = pd.read_excel(SOURCE)
    vcol = (
        raw["Version"].astype(str).str.strip().str.replace(r"^\d+\s*", "", regex=True)
    )
    raw = raw.copy()
    raw["Version"] = vcol
    # Keep: true result, all Apr12 scenarios that have Pct
    want_prefix = [
        "True Election Result",
        "Apr12 final Data, 74% TO, Base Case",
        "Apr12 final Data, 80% TO, VLikely Voters",
        "Apr12 final Data, 80% TO",
    ]
    rows = []
    for w in want_prefix:
        part = raw[raw["Version"] == w]
        for _, r in part.iterrows():
            if pd.isna(r.get("Pct")):
                continue
            rows.append(
                {
                    "Version": w,
                    "Party": r["Party"],
                    "Pct": float(r["Pct"]),
                    "Source": "Augur (internal) / OEVK extract" if w != "True Election Result" else "Official result",
                }
            )
    return pd.DataFrame(rows)


def build() -> None:
    parts: list[pd.DataFrame] = []
    parts.append(load_internal_augur_and_true())
    for label, a, b, c, d, e, o in WIKI_POLLS:
        parts.append(pd.DataFrame(_to_long(label, a, b, c, d, e, o)))
    out = pd.concat(parts, ignore_index=True)
    # Widen: optional seat columns from original for internal rows (optional, leave NaN for wiki)
    for col in [
        "Direct Mandates",
        "List Mandates",
        "Total Mandates",
    ]:
        out[col] = np.nan
    out.to_excel(OUT_XLSX, index=False)
    print(f"Wrote {OUT_XLSX}  ({len(out)} rows, {out['Version'].nunique()} versions).")


if __name__ == "__main__":
    build()
