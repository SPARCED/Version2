#!/usr/bin/env python3
"""Fill rppa-measurements.tsv from MDD Level 3 RPPA data.

Reproduces the statistical transforms in
``Wrangling Level 3 RPPA data.ipynb``:

1. Inverse log2 (``2 ** x``)
2. Mean across replicates that share a specimen-name prefix (split on ``_C1_``)
3. Keep EGF / HGF / IFNG / PBS, copy ``ctrl_0`` onto each ligand's t=0
4. Scale each antibody by its maximum across the remaining 24 columns

Existing filled measurement values are left unchanged and checked against
the reproduced table. Empty rows for new observables are filled.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
LEVEL3_PATH = HERE / "MDD_RPPA_Level3.csv"
SPECIMEN_ANN_PATH = HERE / "42003_2022_3975_MOESM25_ESM.xlsx"
ANTIBODY_ANN_PATH = HERE / "MDD_RPPA_antibodyAnnotations.csv"
MEASUREMENTS_PATH = HERE / "rppa-measurements.tsv"

DROP_LIGANDS = ("BMP2", "TGFB", "OSM")
KEEP_LIGANDS = ("EGF", "HGF", "IFNG", "PBS")
HOURS = (0, 1, 4, 8, 24, 48)
HOUR_TO_SECONDS = {0: 0, 1: 3600, 4: 14400, 8: 28800, 24: 86400, 48: 172800}
LIGAND_TO_CONDITION = {
    "EGF": "EGF",
    "HGF": "HGF only",
    "IFNG": "IFNG_EGF",
    "PBS": "PBS only",
}

# Antibody name or annotation gene symbol -> observable gene used in
# rppa-observables.tsv. Covers annotation errors and legacy gene names.
GENE_OVERRIDES = {
    "XBP-1": "XBP1",
    "HSP27": "HSPB1",
    "Cox2": "PTGS2",
    "PDHK1": "PDHK1",
    "PDGFR-b": "PDGFRB",
    "PDGFR": "PDGFRB",
    "Aurora-B": "AURKB",
    "AIM1": "AURKB",
    "CDK1": "CDK1",
    "CDC2": "CDK1",
    "CD29": "ITGB1",
    "TTF1": "NKX2-1",
    "RIP": "RIPK1",
    "TIGAR": "TIGAR",
    "C12ORF5": "TIGAR",
    "Histone-H3": "H3-4",
    "HIST3H3": "H3-4",
}

PTM_NAME_RE = re.compile(
    r"(_p[STY]\d|_pY\d|cleaved|DM-|U-Histone|P-Met)",
    re.IGNORECASE,
)
MDD_SUFFIX_RE = re.compile(r"-[A-Z]-[A-Z]$")


def load_scaled_antibodies() -> pd.DataFrame:
    """Return antibodies x 24 condition_time columns, max-scaled to (0, 1]."""
    level_3 = pd.read_csv(LEVEL3_PATH, index_col=0)
    annotations = pd.read_excel(SPECIMEN_ANN_PATH)

    level_3 = 2.0 ** level_3

    id_to_name = dict(
        zip(annotations["specimenID"].astype(str), annotations["specimenName"])
    )
    missing = [c for c in level_3.columns if c not in id_to_name]
    if missing:
        raise SystemExit(f"Specimen annotations missing for columns: {missing[:5]}")
    level_3.columns = [id_to_name[c] for c in level_3.columns]

    grouped: dict[str, list[str]] = {}
    for specimen_name in level_3.columns:
        condition = specimen_name.split("_C1_")[0]
        grouped.setdefault(condition, []).append(specimen_name)
    averaged = pd.DataFrame(
        {cond: level_3[cols].mean(axis=1) for cond, cols in grouped.items()}
    )

    drop_cols = [f"{lig}_{t}" for lig in DROP_LIGANDS for t in (1, 4, 8, 24, 48)]
    df_ext = averaged.drop(columns=drop_cols)
    ctrl = df_ext.iloc[:, 0]
    df_ctrless = df_ext.drop(columns=df_ext.columns[0])

    # Match the notebook insert: range is evaluated once on the 20-column frame.
    n_cols = df_ctrless.shape[1]
    for column in range(0, n_cols, 6):
        column_name = df_ctrless.columns[column]
        df_ctrless.insert(column, f"{column_name}_0", ctrl)
    df_ctrless = df_ctrless.rename(
        columns=lambda c: c.replace("_1_0", "_0") if str(c).endswith("_1_0") else c
    )

    ordered = [f"{lig}_{t}" for lig in KEEP_LIGANDS for t in HOURS]
    missing_cols = [c for c in ordered if c not in df_ctrless.columns]
    if missing_cols:
        raise SystemExit(f"Missing wrangled columns: {missing_cols}")
    table = df_ctrless[ordered].copy()
    return table.div(table.max(axis=1), axis=0)


def is_ptm_antibody(antibody: str, sites: object) -> bool:
    if PTM_NAME_RE.search(str(antibody)):
        return True
    sites_s = "" if pd.isna(sites) else str(sites).strip()
    if sites_s in {"", "NA", "nan", "NaN"}:
        return False
    return bool(re.search(r"[STY]\d", sites_s))


def load_antibody_symbols() -> dict[str, list[str]]:
    ann = pd.read_csv(ANTIBODY_ANN_PATH)
    symbols: dict[str, list[str]] = {}
    for rec in ann.itertuples(index=False):
        name = MDD_SUFFIX_RE.sub("", str(rec.MDD))
        raw = rec.Symbols
        genes = [] if pd.isna(raw) else str(raw).replace("|", " ").split()
        symbols[name] = genes
    return symbols


def empty_observable_ids(measurement_rows: list[list[str]]) -> set[str]:
    """Observables that exist in the measurement table but have no values yet."""
    has_value: dict[str, bool] = {}
    for row in measurement_rows:
        if len(row) < 4:
            continue
        oid = row[0]
        if oid == "blank":
            continue
        filled = bool(row[3].strip())
        has_value[oid] = has_value.get(oid, False) or filled
    return {oid for oid, filled in has_value.items() if not filled}


def load_annotation_sites() -> dict[str, object]:
    ann = pd.read_csv(ANTIBODY_ANN_PATH)
    sites = {}
    for rec in ann.itertuples(index=False):
        name = MDD_SUFFIX_RE.sub("", str(rec.MDD))
        sites[name] = rec.Sites
    return sites


def map_new_antibodies(
    antibodies: pd.Index,
    empty_obs: set[str],
) -> dict[str, str]:
    symbols = load_antibody_symbols()
    sites_map = load_annotation_sites()
    mapping: dict[str, str] = {}
    used: dict[str, str] = {}
    for antibody in antibodies:
        genes = symbols.get(antibody, [])
        if antibody in GENE_OVERRIDES:
            genes = [GENE_OVERRIDES[antibody]]
        else:
            genes = [GENE_OVERRIDES.get(g, g) for g in genes]
        if is_ptm_antibody(antibody, sites_map.get(antibody)):
            continue
        candidates = [f"{g} abundance" for g in genes if f"{g} abundance" in empty_obs]
        if not candidates:
            continue
        if len(candidates) > 1:
            raise SystemExit(f"{antibody} maps to multiple new observables: {candidates}")
        oid = candidates[0]
        if oid in used:
            raise SystemExit(
                f"Observable {oid!r} mapped from both {used[oid]!r} and {antibody!r}"
            )
        mapping[antibody] = oid
        used[oid] = antibody
    return mapping


def format_measurement(value: float) -> str:
    if abs(value - 1.0) < 1e-12:
        return "1"
    return f"{value:.9f}".rstrip("0").rstrip(".")


def measurement_lookup(scaled: pd.DataFrame, antibody_to_obs: dict[str, str]) -> dict[tuple[str, str, str], str]:
    """(observableId, simulationConditionId, time) -> formatted measurement."""
    lookup: dict[tuple[str, str, str], str] = {}
    for antibody, oid in antibody_to_obs.items():
        row = scaled.loc[antibody]
        for lig in KEEP_LIGANDS:
            condition = LIGAND_TO_CONDITION[lig]
            for hour in HOURS:
                key = (oid, condition, str(HOUR_TO_SECONDS[hour]))
                lookup[key] = format_measurement(float(row[f"{lig}_{hour}"]))
    return lookup


def read_measurements() -> tuple[list[str], list[list[str]]]:
    with MEASUREMENTS_PATH.open(newline="") as handle:
        rows = list(csv.reader(handle, delimiter="\t"))
    return rows[0], rows[1:]


def repair_missing_conditions(rows: list[list[str]]) -> int:
    """Fill blank simulationConditionId when it is the only missing combo."""
    conditions = list(LIGAND_TO_CONDITION.values())
    n_fixed = 0
    for row in rows:
        if len(row) != 5 or row[0] == "blank" or row[2] != "" or row[3] == "":
            continue
        oid, time = row[0], str(int(float(row[4])))
        present = {
            r[2]
            for r in rows
            if len(r) == 5 and r[0] == oid and r[2] != "" and str(int(float(r[4]))) == time
        }
        missing = [c for c in conditions if c not in present]
        if len(missing) == 1:
            row[2] = missing[0]
            n_fixed += 1
    return n_fixed


def fill_rows(rows: list[list[str]], lookup: dict[tuple[str, str, str], str]) -> int:
    n_filled = 0
    for row in rows:
        if len(row) != 5:
            continue
        oid, _preeq, condition, measurement, time = row
        if oid == "blank" or measurement != "":
            continue
        value = lookup.get((oid, condition, str(int(float(time)))))
        if value is None:
            continue
        row[3] = value
        n_filled += 1
    return n_filled


def write_measurements(header: list[str], rows: list[list[str]]) -> None:
    with MEASUREMENTS_PATH.open("w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)


def verify_existing(scaled: pd.DataFrame, rows: list[list[str]]) -> None:
    """Check filled benchmark values against the reproduced antibody table."""
    filled: dict[str, dict[str, float]] = {}
    for row in rows:
        if len(row) != 5 or row[0] == "blank" or row[3] == "":
            continue
        oid, _preeq, condition, measurement, time = row
        if condition == "":
            print(
                f"WARNING: {oid} at t={time} has an empty simulationConditionId "
                f"(measurement={measurement})"
            )
            continue
        seconds = int(float(time))
        hour = next((h for h, s in HOUR_TO_SECONDS.items() if s == seconds), None)
        lig = next((l for l, c in LIGAND_TO_CONDITION.items() if c == condition), None)
        if hour is None or lig is None:
            continue
        filled.setdefault(oid, {})[f"{lig}_{hour}"] = float(measurement)

    columns = [f"{lig}_{t}" for lig in KEEP_LIGANDS for t in HOURS]
    n_ok = 0
    mismatches = []
    for oid, values in filled.items():
        if len(values) != 24:
            mismatches.append((oid, f"has {len(values)}/24 filled points", None, None))
            continue
        target = pd.Series({c: values[c] for c in columns})
        best_ab = None
        best_diff = None
        for antibody, row in scaled.iterrows():
            diff = float((row[columns] - target).abs().max())
            if best_diff is None or diff < best_diff:
                best_diff = diff
                best_ab = antibody
        if best_diff is not None and best_diff < 1e-6:
            n_ok += 1
        else:
            mismatches.append((oid, best_ab, best_diff, None))

    print(f"Existing observables reproduced within 1e-6: {n_ok}/{len(filled)}")
    for oid, best_ab, best_diff, _ in mismatches:
        print(f"  MISMATCH {oid}: nearest {best_ab} max abs diff={best_diff}")


def verify_new(scaled: pd.DataFrame, rows: list[list[str]], antibody_to_obs: dict[str, str]) -> None:
    obs_to_ab = {oid: ab for ab, oid in antibody_to_obs.items()}
    n_checked = 0
    n_ok = 0
    for oid, antibody in obs_to_ab.items():
        got = {}
        for row in rows:
            if len(row) != 5 or row[0] != oid or row[3] == "":
                continue
            seconds = int(float(row[4]))
            hour = next(h for h, s in HOUR_TO_SECONDS.items() if s == seconds)
            lig = next(l for l, c in LIGAND_TO_CONDITION.items() if c == row[2])
            got[f"{lig}_{hour}"] = float(row[3])
        if len(got) != 24:
            print(f"  NEW incomplete {oid}: {len(got)}/24 from {antibody}")
            continue
        n_checked += 1
        expected = scaled.loc[antibody]
        diffs = [abs(got[c] - float(expected[c])) for c in expected.index]
        max_diff = max(diffs)
        if max_diff < 5e-10:
            n_ok += 1
        else:
            print(f"  NEW mismatch {oid} ({antibody}) max abs diff={max_diff}")
        if abs(max(got.values()) - 1.0) > 1e-12:
            print(f"  NEW {oid} max is {max(got.values())}, expected 1")
    print(f"New observables filled and matching source antibody: {n_ok}/{n_checked}")


def main() -> None:
    print("Wrangling Level 3 RPPA...")
    scaled = load_scaled_antibodies()
    print(f"  {len(scaled)} antibodies x {scaled.shape[1]} condition-time columns")

    header, rows = read_measurements()
    empty_obs = empty_observable_ids(rows)
    antibody_to_obs = map_new_antibodies(scaled.index, empty_obs)
    unused = sorted(empty_obs - set(antibody_to_obs.values()))
    print(f"  mapping {len(antibody_to_obs)} antibodies -> new observables")
    if unused:
        print(f"  no antibody mapped for: {unused}")

    print("\nVerification against existing filled benchmark values:")
    n_repaired = repair_missing_conditions(rows)
    if n_repaired:
        print(f"  repaired {n_repaired} row(s) with blank simulationConditionId")
    verify_existing(scaled, rows)

    lookup = measurement_lookup(scaled, antibody_to_obs)
    n_filled = fill_rows(rows, lookup)
    write_measurements(header, rows)
    print(f"\nFilled {n_filled} previously empty measurement cells in {MEASUREMENTS_PATH.name}")

    print("\nVerification of newly filled observables:")
    verify_new(scaled, rows, antibody_to_obs)

    # Spot-check the notebook example: EIF4EBP1 PBS 1 h == 1
    for row in rows:
        if (
            len(row) == 5
            and row[0] == "EIF4EBP1 abundance"
            and row[2] == "PBS only"
            and row[4] in {"3600", "3600.0"}
        ):
            print(f"\nSpot check EIF4EBP1 abundance / PBS only / 3600 s = {row[3]}")
            break


if __name__ == "__main__":
    main()
