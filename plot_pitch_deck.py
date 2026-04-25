#!/usr/bin/env python3
"""
Pitch-deck figures: 2026 Hungarian parliamentary election — *national party list* vote
share. Uses Augur’s **likely-voter** internal scenario plus a small set of public
benchmarks (including Atlas Intel, as reported by the pollster and secondary sources).

Run after `build_headline_workbook.py` (or with `Headline Predictions (1).xlsx` only,
if combined workbook is missing).
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
    ROOT / "Headline_Predictions_Combined_2026.xlsx",
    ROOT / "Headline Predictions (1).xlsx",
]

PARTIES = ["Tisza", "Fidesz", "MH", "MKKP", "DK"]

# Internal key in workbook → short legend label (deck order: official, ours, then peers)
# Atlas Intel: fieldwork 5–10 Apr 2026, n≈1,587 (AtlasIntel.org); headline figures align with PolitPro.
PITCH_COMPARISON: list[tuple[str, str, str]] = [
    ("True Election Result", "Official list vote (12 Apr 2026)", "#212121"),
    (
        "Apr12 final Data, 80% TO, VLikely Voters",
        "Augur — likely-voter model (12 Apr 2026)",
        "#0D47A1",
    ),
    (
        "Atlas Intel (10 Apr 2026) — reported aggregate",
        "Atlas Intel (5–10 Apr 2026, n≈1,600)",
        "#4A148C",
    ),
    (
        "Publicus (7–9 Apr 2026)",
        "Publicus (7–9 Apr 2026)",
        "#1B5E20",
    ),
    (
        "McLaughlin & Associates (7 Apr 2026)",
        "McLaughlin & Associates (7 Apr 2026)",
        "#B71C1C",
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
            "font.size": 13,
            "axes.titlesize": 16,
            "axes.labelsize": 14,
            "xtick.labelsize": 12,
            "ytick.labelsize": 12,
            "legend.fontsize": 11,
            "legend.title_fontsize": 12,
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
    raise SystemExit("No xlsx found. Add Headline_Predictions_Combined_2026.xlsx or Headline Predictions (1).xlsx.")


def plot_list_vote_comparison(data: dict[str, pd.Series], out: Path) -> None:
    _setup_matplotlib()
    present = [
        (k, lab, c)
        for (k, lab, c) in PITCH_COMPARISON
        if k in data
    ]
    n_series = len(present)
    n_parties = len(PARTIES)
    x = np.arange(n_parties, dtype=float)
    total_w = 0.78
    bar_w = min(total_w / max(n_series, 1), 0.16)
    offset0 = -((n_series - 1) * bar_w) / 2

    fig, ax = plt.subplots(figsize=(15.0, 7.2), facecolor="white")
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
    ax.set_xticklabels(PARTIES, fontweight="bold", fontsize=13)
    ax.set_ylabel("Share of list vote (%)  —  decided / attributed responses", labelpad=10)
    ax.set_ylim(0, 62)
    title = (
        "2026 Hungarian parliamentary election\n"
        "National party list vote (headline shares — comparison to selected public polls)"
    )
    ax.set_title(title, fontweight="bold", pad=16, fontsize=16)
    ax.legend(
        loc="upper right",
        frameon=True,
        framealpha=0.98,
        edgecolor="#CCCCCC",
        title="Scenarios and benchmarks",
    )
    fig.text(
        0.5,
        0.02,
        "Undecided / non-response excluded where pollsters provide headline shares. Public polls: see English Wikipedia 2026 polling table; Atlas Intel fieldwork 5–10 Apr 2026 (atlasintel.org).",
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
        print("Error: need official result for error chart.", file=sys.stderr)
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
    total_w = 0.78
    bar_w = min(total_w / max(n_series, 1), 0.16)
    offset0 = -((n_series - 1) * bar_w) / 2

    fig, ax = plt.subplots(figsize=(15.0, 6.6), facecolor="white")
    ax.axhline(0, color="#333", linewidth=1.1, zorder=2)
    for i, (key, label, color) in enumerate(present):
        err = (data[key] * 100.0) - true
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
    ax.set_xticklabels(PARTIES, fontweight="bold", fontsize=13)
    ax.set_ylabel("Error vs. official list result (percentage points)", labelpad=10)
    m = 0.0
    for key, _, _ in present:
        m = max(m, float(np.nanmax(np.abs((data[key] * 100.0) - true))))
    lim = max(8.0, m * 1.12)
    ax.set_ylim(-lim, lim)
    ax.set_title(
        "Headline error vs. official 12 Apr 2026 list result\n(negative = under-estimated, positive = over-estimated)",
        fontweight="bold",
        pad=16,
        fontsize=16,
    )
    ax.legend(
        loc="upper right",
        frameon=True,
        framealpha=0.98,
        edgecolor="#CCCCCC",
        title="Model / poll (same labels as list-vote figure)",
    )
    fig.text(
        0.5,
        0.02,
        "Benchmark is the final national list vote (same party buckets as the model).",
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
            print(f"Missing: {key}", file=sys.stderr)
    out1 = PLOTS / "2026_hungary_list_vote_pitch.png"
    out2 = PLOTS / "2026_hungary_list_vote_error_pitch.png"
    plot_list_vote_comparison(data, out1)
    plot_error_vs_official(data, out2)
    print(f"Wrote {out1}")
    print(f"Wrote {out2}")


if __name__ == "__main__":
    main()
