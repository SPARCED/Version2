#!/usr/bin/env python3
"""RNASeq paired heatmap: HECM (left) vs experimental RNA-seq (right).

Uses the slim Benchtop pickle from
``scripts/select_rnaseq_heatmap_observables.py``.

Simulation values are treated as nM, averaged across replicate cells, then
converted to molecules/cell using Avogadro's number and the per-species
compartment volume from ``model/Compartments-v1.2.tsv`` (parsed from each
observable formula). Experiment is already in copy numbers. Both panels are
then divided per observable by that observable's t0 value (experiment uses
the shared control t0; simulation uses the mean of its own t0 cells) and
share a fold-change-vs-t0 color scale.

    python scripts/select_rnaseq_heatmap_observables.py
    python benchmarks/LINCS-RNASeq/plot_rnaseq_heatmaps.py
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / "notebooks"))

from lincs_paired_heatmap import (  # noqa: E402
    DEFAULT_CONDITION_ORDER,
    load_observable_labels,
    load_pickle,
    pickle_runs_to_frame,
    pivot_condition_time,
    plot_paired_heatmaps,
    prepare_pickle_frame,
)

N_A = 6.022e23
COMPARTMENT_RE = re.compile(r"^(?P<tag>cyt|mit|nuc)_")
COMPARTMENTS_TSV = REPO / "model" / "Compartments-v1.2.tsv"
OBSERVABLES_TSV = HERE / "rnaseq-observables.tsv"
SLIM_PKL = HERE / "LINCS-RNASeq-heatmap500.pkl"
OUT_PNG = HERE / "figures" / "HECM-vs-RNASeq-heatmap.png"


def load_volumes(path: Path) -> dict[str, float]:
    """Map fieldId (cyt/mit/nuc/...) -> volume in liters."""
    volumes: dict[str, float] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            tag = (row.get("fieldId") or "").strip()
            vol = row.get("volume")
            if tag and vol not in (None, ""):
                volumes[tag] = float(vol)
    return volumes


def nm_to_copies_factor(volume_L: float) -> float:
    """copies = nM * 1e-9 mol/L * V_L * N_A."""
    return N_A * 1e-9 * volume_L


def observable_volume_factors(
    observables_path: Path, volumes: dict[str, float]
) -> dict[str, float]:
    """observableId -> nM-to-copies factor from formula compartment tag."""
    factors: dict[str, float] = {}
    default_vol = volumes.get("cyt")
    if default_vol is None:
        raise KeyError("Cytoplasm (cyt) volume missing from compartments table")
    default_factor = nm_to_copies_factor(default_vol)

    with observables_path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            obs_id = (row.get("observableId") or "").strip()
            formula = (row.get("observableFormula") or "").strip()
            if not obs_id or obs_id == "blank":
                continue
            match = COMPARTMENT_RE.match(formula)
            if match:
                tag = match.group("tag")
                if tag not in volumes:
                    raise KeyError(f"No volume for compartment tag {tag!r} ({obs_id})")
                factors[obs_id] = nm_to_copies_factor(volumes[tag])
            else:
                factors[obs_id] = default_factor
    return factors


def divide_rows_by_t0(matrix: pd.DataFrame) -> pd.DataFrame:
    """Divide each observable row by the mean of its t0 (time == 0) cells.

    Zero or non-finite t0 values become NaN so those rows do not produce inf.
    """
    if matrix.empty:
        return matrix.astype(float)
    t0_cols = [col for col in matrix.columns if float(col[1]) == 0.0]
    if not t0_cols:
        raise ValueError("No t0 (time == 0) columns to normalize against")
    t0 = matrix.loc[:, t0_cols].astype(float).mean(axis=1)
    t0 = t0.where(np.isfinite(t0.to_numpy(dtype=float)) & (t0 != 0))
    return matrix.astype(float).div(t0, axis=0)


def build_t0_normalized_matrices(
    pickle_path: Path,
    observables_path: Path,
    volumes_path: Path,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, str], dict]:
    runs = load_pickle(pickle_path)
    frame = prepare_pickle_frame(pickle_runs_to_frame(runs))
    if frame.empty:
        raise ValueError(f"No experiment/simulation rows in {pickle_path}")

    experiment = pivot_condition_time(frame, "experiment", DEFAULT_CONDITION_ORDER)
    simulation = pivot_condition_time(frame, "simulation", DEFAULT_CONDITION_ORDER)
    keep_cols = [
        col
        for col in experiment.columns
        if np.isfinite(experiment[col].to_numpy(dtype=float)).any()
    ]
    experiment = experiment.loc[:, keep_cols]
    simulation = simulation.reindex(columns=keep_cols)

    exp = divide_rows_by_t0(experiment)

    volumes = load_volumes(volumes_path)
    factors = observable_volume_factors(observables_path, volumes)
    sim = simulation.astype(float).copy()
    for obs_id in sim.index:
        sim.loc[obs_id] = sim.loc[obs_id] * factors.get(
            str(obs_id), nm_to_copies_factor(volumes["cyt"])
        )
    sim = divide_rows_by_t0(sim)

    labels = load_observable_labels(observables_path, fallback_ids=experiment.index)
    sim_vals = sim.to_numpy(dtype=float)
    exp_vals = exp.to_numpy(dtype=float)
    info = {
        "n_runs": len(runs),
        "n_pickle_observables": int(frame["observableId"].nunique()),
        "n_observables": int(exp.shape[0]),
        "n_columns": int(exp.shape[1]),
        "has_simulation": bool(np.isfinite(sim_vals).any()),
        "has_experiment": bool(np.isfinite(exp_vals).any()),
        "volumes": volumes,
        "sim_fc_min": float(np.nanmin(sim_vals)) if np.isfinite(sim_vals).any() else np.nan,
        "sim_fc_max": float(np.nanmax(sim_vals)) if np.isfinite(sim_vals).any() else np.nan,
        "exp_fc_min": float(np.nanmin(exp_vals)) if np.isfinite(exp_vals).any() else np.nan,
        "exp_fc_max": float(np.nanmax(exp_vals)) if np.isfinite(exp_vals).any() else np.nan,
    }
    return sim, exp, labels, info


def main() -> None:
    if not SLIM_PKL.exists():
        raise SystemExit(
            f"Missing {SLIM_PKL.name}. Run:\n"
            f"  python scripts/select_rnaseq_heatmap_observables.py"
        )

    simulation, experiment, labels, info = build_t0_normalized_matrices(
        SLIM_PKL, OBSERVABLES_TSV, COMPARTMENTS_TSV
    )
    print(
        f"Runs: {info['n_runs']}; pickle observables: {info['n_pickle_observables']}; "
        f"matrix {info['n_observables']} x {info['n_columns']}; "
        f"simulation finite={info['has_simulation']}; experiment finite={info['has_experiment']}"
    )
    print(f"Compartment volumes (L): {info['volumes']}")
    print(
        f"Fold-change vs t0 — sim [{info['sim_fc_min']:.4g}, {info['sim_fc_max']:.4g}], "
        f"exp [{info['exp_fc_min']:.4g}, {info['exp_fc_max']:.4g}]"
    )

    stacked = np.concatenate(
        [
            simulation.to_numpy(dtype=float).ravel(),
            experiment.to_numpy(dtype=float).ravel(),
        ]
    )
    finite = stacked[np.isfinite(stacked)]
    vmax = float(np.nanmax(finite)) if finite.size else 1.0
    print(f"Shared color scale: vmin=0, vmax={vmax:.4g} (fold change vs t0)")

    plot_paired_heatmaps(
        simulation,
        experiment,
        labels=labels,
        sim_title="HECM",
        exp_title="RNASeq",
        cmap="crest",
        vmin=0.0,
        vmax=vmax,
        cbar_label="fold change vs t0",
        output=OUT_PNG,
    )


if __name__ == "__main__":
    main()
