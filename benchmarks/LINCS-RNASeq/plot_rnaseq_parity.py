#!/usr/bin/env python3
"""RNASeq parity plots: experiment (counts) vs HECM simulation (MPC).

Replicate cells are averaged first. Simulation stays in nM until that average,
then is converted to molecules/cell. No other scaling. One panel per condition;
point color goes light to dark with time.

    python benchmarks/LINCS-RNASeq/plot_rnaseq_parity.py
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from tkinter import N

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "notebooks"))

from lincs_paired_heatmap import (  # noqa: E402
    DEFAULT_CONDITION_ORDER,
    load_pickle,
)
from plot_rnaseq_clustermap import simulation_nM_to_copies  # noqa: E402
from plot_rnaseq_heatmaps import COMPARTMENTS_TSV  # noqa: E402
from select_rnaseq_heatmap_observables import (  # noqa: E402
    stream_mean_experiment_matrix,
    stream_mean_simulation_matrix,
)

DEFAULT_PKL = HERE / "LINCS-RNASeq.pkl"
OBSERVABLES_TSV = HERE / "rnaseq-observables.tsv"
OUT_PNG = HERE / "figures" / "HECM-vs-RNASeq-parity.png"


def aligned_copy_matrices(
    runs: dict,
    observables_path: Path,
    volumes_path: Path,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    experiment = stream_mean_experiment_matrix(runs)
    simulation = stream_mean_simulation_matrix(runs)
    if experiment.empty or simulation.empty:
        raise ValueError("Pickle is missing experiment or simulation values")
    simulation = simulation_nM_to_copies(
        simulation, observables_path, volumes_path
    )
    experiment, simulation = experiment.align(simulation, join="inner")
    return experiment.astype(float), simulation.astype(float)


def plot_parity(
    experiment: pd.DataFrame,
    simulation: pd.DataFrame,
    output: Path,
) -> None:
    conditions = [
        cond
        for cond in DEFAULT_CONDITION_ORDER
        if cond in experiment.columns.get_level_values("conditionId")
    ]
    extra = sorted(
        set(experiment.columns.get_level_values("conditionId")) - set(conditions)
    )
    conditions.extend(extra)
    times = sorted({float(t) for _, t in experiment.columns})

    stacked = np.concatenate(
        [
            np.log10(experiment.to_numpy(dtype=float).ravel()),
            np.log10(simulation.to_numpy(dtype=float).ravel()),
        ]
    )
    finite = stacked[np.isfinite(stacked)]
    vmax = float(np.nanmax(finite)) if finite.size else 1.0
    vmax = max(vmax, 1.0)

    colors = plt.cm.Reds(np.linspace(0.25, 0.95, max(len(times), 1)))
    time_to_color = dict(zip(times, colors))
    time_labels = {t: f"{t / 3600:g}h" for t in times}

    fig, axes = plt.subplots(2, 2, figsize=(12, 12), layout="constrained")
    axes = np.atleast_1d(axes).ravel()

    for ax, cond in zip(axes, conditions):
        xs, ys = [], []
        for t in times:
            if (cond, t) not in experiment.columns:
                continue
            x_raw = experiment[(cond, t)].to_numpy(dtype=float)
            y_raw = simulation[(cond, t)].to_numpy(dtype=float)
            keep = (x_raw > 0) & (y_raw > 0) & np.isfinite(x_raw) & np.isfinite(y_raw)
            x = np.log10(x_raw[keep])
            y = np.log10(y_raw[keep])
            
            ax.scatter(
                x,
                y,
                s=10,
                alpha=0.45,
                c=[time_to_color[t]],
                edgecolors="none",
                label=time_labels[t],
                rasterized=True,
            )
            xs.append(x)
            ys.append(y)
        ax.plot([0, vmax], [0, vmax], "k--", linewidth=1, alpha=0.5)
        x_all = np.concatenate(xs)
        y_all = np.concatenate(ys)
        model = LinearRegression()
        model.fit(x_all.reshape(-1, 1), y_all.reshape(-1, 1))
        y_pred = model.predict(x_all.reshape(-1, 1))
        
        # Calculate the R-squared value
        r2 = r2_score(y_all.reshape(-1, 1), y_pred)
        ax.text(0.25, 0.95, f"R² = {r2:.2f}", transform=ax.transAxes, fontsize=10, verticalalignment="top", horizontalalignment="left")
        #ax.set_xlim(0, vmax)
        #ax.set_ylim(0, vmax)
        #ax.set_aspect("equal")
        ax.set_title(cond, weight="bold", fontsize=16)
        ax.set_xlabel(r'$log_{10}$(RNASeq experiment (counts)', fontsize=16, fontweight="bold")
        ax.set_ylabel(r'$log_{10}$(EpiC simulation (counts)', fontsize=16, fontweight="bold")
        ax.legend(title="time", fontsize=8, loc="upper left", frameon=False)

    for ax in axes[len(conditions):]:
        ax.set_visible(False)

    # fig.suptitle("EpiC vs RNASeq parity (copy number)", fontsize=14)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {output}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pkl", type=Path, default=DEFAULT_PKL)
    parser.add_argument("--observables", type=Path, default=OBSERVABLES_TSV)
    parser.add_argument("--volumes", type=Path, default=COMPARTMENTS_TSV)
    parser.add_argument("--out", type=Path, default=OUT_PNG)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    if not args.pkl.exists():
        raise SystemExit(f"Missing pickle: {args.pkl}")

    print(f"Loading {args.pkl} ...", flush=True)
    runs = load_pickle(args.pkl)
    print("Averaging replicates; converting simulation nM to copies ...", flush=True)
    experiment, simulation = aligned_copy_matrices(
        runs, args.observables, args.volumes
    )
    print(
        f"Parity: {experiment.shape[0]} observables x {experiment.shape[1]} "
        "condition-time columns",
        flush=True,
    )
    plot_parity(experiment, simulation, args.out)


if __name__ == "__main__":
    main()
