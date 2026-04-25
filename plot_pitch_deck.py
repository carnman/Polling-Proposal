#!/usr/bin/env python3
"""
Pitch-deck figures: 2026 Hungarian parliamentary election — *national party list* vote
share. Compares the official **list** result, Augur **likely-voter** model, 21 Kutatóközpont,
Medián, and Alapjogokért Központ (government-aligned), per the English Wikipedia 2026 table.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
PLOTS = ROOT / "plots"
PLOTS.mkdir(exist_ok=True)

DATA_CANDIDATES = [
    ROOT / "headline_pitch_data.xlsx",
    ROOT / "Headline_Predictions_Combined_2026.xlsx",
    ROOT / "Headline Predictions (1).xlsx",
]

PARTIES = ["Tisza", "Fidesz", "MH", "MKKP", "DK"]

# Workbook Version string → legend label, color (order: result, us, then peers)
PITCH_COMPARISON: list[tuple[str, str, str]] = [
    (
        "True Election Result",
        "Official list vote (NVI; Wikipedia party-list %)",
        "#212121",
    ),
    (
        "Apr12 final Data, 80% TO, VLikely Voters",
        "Augur — likely-voter model (12 Apr 2026)",
        "#0D47A1",
    ),
    (
        "Kutatóközpont (21 Research) (8–11 Apr 2026)",
        "Kutatóközpont / 21 Research (8–11 Apr 2026)",
        "#00695C",
    ),
    (
        "Medián (7–11 Apr 2026)",
        "Medián (7–11 Apr 2026, n=2,286)",
        "#6A1B9A",
    ),
    (
        "Alapjogokért Központ (28–29 Mar 2026)",
        "Alapjogokért Központ (28–29 Mar; government-leaning)",
        "#E65100",
    ),
]


def _load(path: Path) -> pd.DataFrame:
    df = pd.read_excel(path)
    df["Version"] = (
        df["Version"].astype(str).str.strip().str.replace(r"^\d+\s*", "", regex=True)
    )
    df = df.dropna(subset=["Pct"])
    df["Pct"] = pd.to_numeric(df["Pct"], errors="coerce")
    return df.dropna(subset=["Pct"])


def _pivot_for_versions(df: pd.DataFrame) -> dict[str, pd.Series]:
    out: dict[str, pd.Series] = {}
    for key, _, _ in PITCH_COMPARISON:
        sub = df[df["Version"] == key]
        if sub.empty:
            continue
        s = sub.set_index("Party")["Pct"].reindex(PARTIES)
        out[key] = s
    return out


def _setup_matplotlib() -> None:
    plt.rcParams.update(
        {
            "font.size": 14,
            "axes.titlesize": 17,
            "axes.labelsize": 15,
            "xtick.labelsize": 13,
            "ytick.labelsize": 13,
            "legend.fontsize": 12,
            "legend.title_fontsize": 13,
            "figure.facecolor": "white",
            "axes.facecolor": "#FAFAFA",
            "axes.grid": True,
            "grid.color": "#E0E0E0",
            "grid.linestyle": "--",
            "grid.linewidth": 0.8,
        }
    )


def _resolve_data() -> Path:
    if os.environ.get("PITCH_DATA"):
        return Path(os.environ["PITCH_DATA"]).expanduser()
    if len(sys.argv) > 1:
        return Path(sys.argv[1])
    for p in DATA_CANDIDATES:
        if p.is_file():
            return p
    raise SystemExit(
        "No data xlsx. Run: python3 build_headline_workbook.py  "
        "(needs Headline Predictions (1).xlsx for the Augur likely-voter row)"
    )


def plot_list_vote_comparison(data: dict[str, pd.Series], out: Path) -> None:
    _setup_matplotlib()
    present = [
        (k, lab, c) for (k, lab, c) in PITCH_COMPARISON if k in data
    ]
    n_series = len(present)
    n_parties = len(PARTIES)
    x = np.arange(n_parties, dtype=float)
    total_w = 0.82
    bar_w = min(total_w / max(n_series, 1), 0.14)
    offset0 = -((n_series - 1) * bar_w) / 2

    fig, ax = plt.subplots(figsize=(16.0, 7.4), facecolor="white")
    for i, (key, label, color) in enumerate(present):
        s = data[key] * 100.0
        xpos = x + offset0 + i * bar_w
        ax.bar(
            xpos,
            s.values,
            width=bar_w * 0.95,
            label=label,
            color=color,
            edgecolor="white",
            linewidth=1.0,
            zorder=3,
        )
    ax.set_xticks(x)
    ax.set_xticklabels(PARTIES, fontweight="bold", fontsize=14)
    ax.set_ylabel(
        "Share of national party list vote (%)  —  headline / decided",
        labelpad=10,
    )
    ax.set_ylim(0, 60)
    title = (
        "2026 Hungarian parliamentary election\n"
        "Party list results vs. our likely-voter model and selected public polls"
    )
    ax.set_title(title, fontweight="bold", pad=16, fontsize=17)
    ax.legend(
        loc="upper right",
        frameon=True,
        framealpha=0.98,
        edgecolor="#CCCCCC",
        title="Benchmarks",
    )
    fig.text(
        0.5,
        0.02,
        "“True” bars use official party list percentages (not constituency SMD shares). Public polls: English Wikipedia, Opinion polling for the 2026 Hungarian parliamentary election (verify against pollster releases).",
        ha="center",
        fontsize=9,
        color="#555555",
    )
    plt.subplots_adjust(bottom=0.12)
    fig.savefig(out, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def plot_error_vs_official(
    data: dict[str, pd.Series],
    out: Path,
) -> None:
    _setup_matplotlib()
    if "True Election Result" not in data:
        print("Error: need True Election Result for error chart.", file=sys.stderr)
        return
    true = data["True Election Result"] * 100.0
    present = [
        (k, lab, c)
        for (k, lab, c) in PITCH_COMPARISON
        if k in data and k != "True Election Result"
    ]
    n_series = len(present)
    n_parties = len(PARTIES)
    x = np.arange(n_parties, dtype=float)
    total_w = 0.82
    bar_w = min(total_w / max(n_series, 1), 0.14)
    offset0 = -((n_series - 1) * bar_w) / 2

    fig, ax = plt.subplots(figsize=(16.0, 6.8), facecolor="white")
    ax.axhline(0, color="#333", linewidth=1.1, zorder=2)
    m = 0.0
    for i, (key, label, color) in enumerate(present):
        err = (data[key] * 100.0) - true
        m = max(m, float(np.nanmax(np.abs(err))))
        xpos = x + offset0 + i * bar_w
        ax.bar(
            xpos,
            err.values,
            width=bar_w * 0.95,
            label=label,
            color=color,
            edgecolor="white",
            linewidth=1.0,
            zorder=3,
        )
    ax.set_xticks(x)
    ax.set_xticklabels(PARTIES, fontweight="bold", fontsize=14)
    ax.set_ylabel("Error vs. official party list result (pp)", labelpad=10)
    lim = max(6.0, m * 1.12)
    ax.set_ylim(-lim, lim)
    ax.set_title(
        "Error vs. official party list vote (12 Apr 2026)\n(negative = under-estimated, positive = over-estimated)",
        fontweight="bold",
        pad=16,
        fontsize=17,
    )
    ax.legend(
        loc="upper right",
        frameon=True,
        framealpha=0.98,
        edgecolor="#CCCCCC",
        title="Model / poll",
        title_fontsize=13,
    )
    fig.text(
        0.5,
        0.02,
        "Reference is the final national party list share for each party (same buckets as the model).",
        ha="center",
        fontsize=9,
        color="#555555",
    )
    plt.subplots_adjust(bottom=0.11)
    fig.savefig(out, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main() -> None:
    path = _resolve_data()
    df = _load(path)
    data = _pivot_for_versions(df)
    for key, _, _ in PITCH_COMPARISON:
        if key not in data:
            print(f"Missing data row: {key}", file=sys.stderr)
    out1 = PLOTS / "2026_hungary_list_vote_pitch.png"
    out2 = PLOTS / "2026_hungary_list_vote_error_pitch.png"
    plot_list_vote_comparison(data, out1)
    plot_error_vs_official(data, out2)
    print(f"Wrote {out1}")
    print(f"Wrote {out2}")


if __name__ == "__main__":
    main()
