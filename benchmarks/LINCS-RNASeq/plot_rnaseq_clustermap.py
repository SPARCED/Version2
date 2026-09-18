#!/usr/bin/env python3
"""Unsupervised hierarchical clustering heatmaps of LINCS RNA-seq.

Experiment: mean replicate counts, shared t0 collapsed to one CTRL 0h column,
t0 fold-change, gene z-score, Ward clustering.

Simulation: mean replicates in nM, convert to copies (MPC), same CTRL collapse
and t0 fold-change, then the same clustering.

    python benchmarks/LINCS-RNASeq/plot_rnaseq_clustermap.py
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "notebooks"))

from lincs_paired_heatmap import (  # noqa: E402
    format_column_labels,
    load_observable_labels,
    load_pickle,
)
from plot_rnaseq_heatmaps import (  # noqa: E402
    COMPARTMENTS_TSV,
    divide_rows_by_t0,
    load_volumes,
    nm_to_copies_factor,
    observable_volume_factors,
)
from select_rnaseq_heatmap_observables import (  # noqa: E402
    stream_mean_experiment_matrix,
    stream_mean_simulation_matrix,
)

DEFAULT_PKL = HERE / "LINCS-RNASeq.pkl"
OBSERVABLES_TSV = HERE / "rnaseq-observables.tsv"
OUT_EXP_PNG = HERE / "figures" / "RNASeq-experiment-clustermap.png"
OUT_EXP_ORDER = HERE / "figures" / "rnaseq_clustermap_gene_order.csv"
OUT_SIM_PNG = HERE / "figures" / "HECM-simulation-clustermap.png"
OUT_SIM_ORDER = HERE / "figures" / "hecm_clustermap_gene_order.csv"
CTRL_COL = ("CTRL", 0.0)


def unique_gene_labels(
    observable_ids: pd.Index, labels: dict[str, str]
) -> dict[str, str]:
    """Map observableId -> unique display name (HGNC, or HGNC plus id)."""
    used: set[str] = set()
    unique: dict[str, str] = {}
    for obs_id in observable_ids:
        key = str(obs_id)
        base = labels.get(key, key)
        name = base if base not in used else f"{base} ({key})"
        used.add(name)
        unique[key] = name
    return unique


def collapse_t0_to_ctrl(matrix: pd.DataFrame) -> pd.DataFrame:
    """Replace per-condition t0 columns with one CTRL 0h column (row-wise mean)."""
    if matrix.empty:
        return matrix.astype(float)
    t0_cols = [col for col in matrix.columns if float(col[1]) == 0.0]
    later_cols = [col for col in matrix.columns if float(col[1]) != 0.0]
    if not t0_cols:
        raise ValueError("No t0 (time == 0) columns to collapse")
    ctrl = matrix.loc[:, t0_cols].astype(float).mean(axis=1)
    ctrl_df = pd.DataFrame(
        {CTRL_COL: ctrl},
        index=matrix.index,
    )
    ctrl_df.columns = pd.MultiIndex.from_tuples(
        [CTRL_COL], names=matrix.columns.names
    )
    later = matrix.loc[:, later_cols].astype(float)
    return pd.concat([ctrl_df, later], axis=1)


def simulation_nM_to_copies(
    simulation: pd.DataFrame,
    observables_path: Path,
    volumes_path: Path,
) -> pd.DataFrame:
    """Convert averaged nM simulation rows to molecules/cell."""
    volumes = load_volumes(volumes_path)
    factors = observable_volume_factors(observables_path, volumes)
    default = nm_to_copies_factor(volumes["cyt"])
    scale = pd.Series(
        {obs_id: factors.get(str(obs_id), default) for obs_id in simulation.index},
        dtype=float,
    )
    return simulation.astype(float).mul(scale, axis=0)


def filter_fold_matrix(fold: pd.DataFrame, max_rows: int = 0) -> pd.DataFrame:
    finite = np.isfinite(fold.to_numpy(dtype=float))
    fold = fold.loc[finite.all(axis=1)]
    std = fold.std(axis=1, skipna=True)
    fold = fold.loc[std.fillna(0.0) > 0]
    if fold.empty:
        raise ValueError("No observables left after t0-normalization")
    if max_rows and max_rows < len(fold):
        keep = std.loc[fold.index].nlargest(max_rows).index
        fold = fold.loc[keep]
        print(f"Subset to {len(fold)} most variable observables", flush=True)
    return fold


def prepare_experiment_matrix(
    runs: dict,
    observables_path: Path,
    max_rows: int = 0,
) -> tuple[pd.DataFrame, dict[str, str]]:
    experiment = stream_mean_experiment_matrix(runs)
    if experiment.empty:
        raise ValueError("No experiment values in pickle")
    fold = divide_rows_by_t0(collapse_t0_to_ctrl(experiment))
    fold = filter_fold_matrix(fold, max_rows=max_rows)
    labels = load_observable_labels(observables_path, fallback_ids=fold.index)
    return fold, unique_gene_labels(fold.index, labels)


def prepare_simulation_matrix(
    runs: dict,
    observables_path: Path,
    volumes_path: Path,
    max_rows: int = 0,
) -> tuple[pd.DataFrame, dict[str, str]]:
    simulation = stream_mean_simulation_matrix(runs)
    if simulation.empty:
        raise ValueError("No simulation values in pickle")
    copies = simulation_nM_to_copies(simulation, observables_path, volumes_path)
    fold = divide_rows_by_t0(collapse_t0_to_ctrl(copies))
    fold = filter_fold_matrix(fold, max_rows=max_rows)
    labels = load_observable_labels(observables_path, fallback_ids=fold.index)
    return fold, unique_gene_labels(fold.index, labels)


def plot_clustermap(
    matrix: pd.DataFrame,
    gene_labels: dict[str, str],
    output: Path,
    order_csv: Path,
    title: str,
) -> None:
    plot_df = matrix.astype(float).copy()
    plot_df.columns = format_column_labels(matrix.columns)

    grid = sns.clustermap(
        plot_df,
        z_score=0,
        row_cluster=True,
        col_cluster=True,
        method="ward",
        metric="euclidean",
        cmap="vlag",
        center=0,
        yticklabels=False,
        xticklabels=True,
        figsize=(12, 16),
        dendrogram_ratio=(0.15, 0.08),
        cbar_kws={"label": "z-scored fold change vs t0"},
        tree_kws={"linewidths": 0.4},
    )
    grid.fig.suptitle(title, weight="bold", fontsize=14, y=1.02)
    grid.ax_heatmap.set_xlabel("")
    grid.ax_heatmap.set_ylabel("mRNA (HGNC order in CSV)")
    grid.ax_heatmap.tick_params(axis="x", labelsize=8)
    for collection in grid.ax_heatmap.collections:
        collection.set_rasterized(True)

    output.parent.mkdir(parents=True, exist_ok=True)
    grid.savefig(output, dpi=200, bbox_inches="tight")
    plt.close(grid.fig)
    print(f"Wrote {output}", flush=True)

    order_csv.parent.mkdir(parents=True, exist_ok=True)
    with order_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["dendrogram_order", "observableId", "gene"])
        for i, obs_id in enumerate(grid.data2d.index):
            key = str(obs_id)
            writer.writerow([i, key, gene_labels.get(key, key)])
    print(f"Wrote {order_csv}", flush=True)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pkl", type=Path, default=DEFAULT_PKL)
    parser.add_argument("--observables", type=Path, default=OBSERVABLES_TSV)
    parser.add_argument("--volumes", type=Path, default=COMPARTMENTS_TSV)
    parser.add_argument("--out", type=Path, default=OUT_EXP_PNG)
    parser.add_argument("--out-order", type=Path, default=OUT_EXP_ORDER)
    parser.add_argument("--out-sim", type=Path, default=OUT_SIM_PNG)
    parser.add_argument("--out-sim-order", type=Path, default=OUT_SIM_ORDER)
    parser.add_argument(
        "--max-rows",
        type=int,
        default=0,
        help="If >0, cluster only this many most variable observables (preview)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    if not args.pkl.exists():
        raise SystemExit(f"Missing pickle: {args.pkl}")

    print(f"Loading {args.pkl} ...", flush=True)
    runs = load_pickle(args.pkl)

    print("Streaming experiment means ...", flush=True)
    experiment, exp_labels = prepare_experiment_matrix(
        runs, args.observables, max_rows=args.max_rows
    )
    print(
        f"Clustering experiment {experiment.shape[0]} x {experiment.shape[1]} "
        "(CTRL 0h + later times; t0 fold-change, gene z-score)",
        flush=True,
    )
    plot_clustermap(
        experiment,
        exp_labels,
        args.out,
        args.out_order,
        title="LINCS RNASeq experiment",
    )

    print("Streaming simulation means (nM), converting to copies ...", flush=True)
    simulation, sim_labels = prepare_simulation_matrix(
        runs, args.observables, args.volumes, max_rows=args.max_rows
    )
    print(
        f"Clustering HECM simulation {simulation.shape[0]} x {simulation.shape[1]} "
        "(MPC; CTRL 0h + later times; t0 fold-change, gene z-score)",
        flush=True,
    )
    plot_clustermap(
        simulation,
        sim_labels,
        args.out_sim,
        args.out_sim_order,
        title="HECM simulation (MPC)",
    )


if __name__ == "__main__":
    main()
