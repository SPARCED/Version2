#!/usr/bin/env python3
"""Remap original SPARCED RPPA observable formulas onto Species-v1.2 IDs.

Only the original 77 observables (rows before ``YWHAB abundance``) are rewritten.
New antibody formulas are left unchanged.

Missing tokens are rewritten with the Species-v1.2 rename patterns, then dropped
if no current ID exists (those terms already evaluated to 0).
"""

from __future__ import annotations

import csv
import io
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
SPECIES_PATH = REPO / "model" / "Species-v1.2.tsv"
OBS_PATH = HERE / "rppa-observables.tsv"
NEW_OBS_START = "YWHAB abundance"

TOKEN_RE = re.compile(r"(?:@[A-Za-z_]+::[A-Za-z_]\w*|[A-Za-z_]\w*)(?:\(\))?")
TERM_RE = re.compile(
    r"(?P<id>[A-Za-z_]\w*)(?:\s*\*\s*(?P<coef>[0-9.]+))?"
)
RECEPTOR_PHOSPHO_RE = re.compile(
    r"(?:p[STY]\d+_)+(?=(?:EGFR|ERBB2|ERBB3|ERBB4|MET|IGF1R|INSR|FGFR))"
)
PS_PREFIX_RE = re.compile(r"(?<=_)P([STY])(\d)")
MISSING_DUNDER_RE = re.compile(r"(_1_)(?!_)(?=(?:EGFR|ERBB2|ERBB3|ERBB4|MET))")
EBP1_ISO_RE = re.compile(r"4EBP1_(?!1_)")
MAPK_COMPONENT_RE = re.compile(r"(?<![A-Z0-9])MAPK_")
IGF1R_ISO_RE = re.compile(r"IGF1R_(?!1_)")
BRAF_ISO_RE = re.compile(r"BRAF_(?!1_)")
PEBP1_ISO_RE = re.compile(r"PEBP1_(?!1_)")
PREFIX_RE = re.compile(
    r"^(?P<comp>cyt|nuc|mit|exc)_(?P<typ>cong|prot|mixed|comp|abs|mrna|gene)(?:_(?P<state>in|a|i))?__"
)
RECEPTOR_COMPONENT_RE = re.compile(
    r"(?<!p_)(?<=__)(?P<rec>EGFR_1_|ERBB2_1_|ERBB3_1_|ERBB4_1_|MET_1_|IGF1R_1_|INSR_1_)"
)

TYPE_FALLBACKS = {
    "mixed": ("cong", "prot", "abs"),
    "prot": ("cong", "mixed", "abs"),
    "cong": ("mixed", "prot", "abs"),
    "comp": ("abs",),
    "abs": ("comp",),
}


def load_species() -> set[str]:
    ids: set[str] = set()
    with SPECIES_PATH.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            ids.add(row["speciesId"])
    return ids


def rewrite_token(token: str) -> str:
    text = token.replace("cyt_prot_in_p", "cyt_prot_in__p")
    text = text.replace("nuc_prot___", "nuc_prot__")
    text = text.replace("cyt_prot___", "cyt_prot__")
    text = MISSING_DUNDER_RE.sub(r"\1_", text)
    text = PS_PREFIX_RE.sub(r"p\1\2", text)
    text = RECEPTOR_PHOSPHO_RE.sub("p_", text)
    text = text.replace("MAP2K", "MEK")
    text = text.replace("p_p_MAPK", "p_p_ERK")
    text = text.replace("p_MAPK", "p_ERK")
    text = MAPK_COMPONENT_RE.sub("ERK_", text)
    text = text.replace("PRKC", "PKC")
    text = text.replace("KPC", "PKC")
    text = IGF1R_ISO_RE.sub("IGF1R_1_", text)
    text = BRAF_ISO_RE.sub("BRAF_1_", text)
    text = PEBP1_ISO_RE.sub("PEBP1_1_", text)
    text = EBP1_ISO_RE.sub("4EBP1_1_", text)
    text = text.replace("PIP3__PDK1_", "PIP3__PDPK1_1_")
    text = text.replace("MTORC1", "RPTOR_1__MTOR_1")
    text = text.replace("MTORC2", "RICTR_1__MTOR_1")
    text = text.replace("APAF_1__PCSK9_1", "APAF_1__CASP9_1")
    text = text.replace("CDK4__CDN", "CDK4and6__CDN")
    text = text.replace("__GTP__TSC_", "__GTP__TSC1_1__TSC2_1_")
    text = text.replace("CDP_DAG__GRP_1_", "CDP_DAG__RASGRP_")
    text = text.replace("KS6B1_1", "S6K")
    text = text.replace("cyt_cong_i__CASP3_", "cyt_cong__CASP3_")
    text = text.replace("cyt_cong_a__CASP3_", "cyt_cong__cl_CASP3_")
    return text


def type_variants(token: str) -> list[str]:
    match = PREFIX_RE.match(token)
    if not match:
        return []
    typ = match.group("typ")
    variants: list[str] = []
    for new_typ in TYPE_FALLBACKS.get(typ, ()):
        variants.append(token[: match.start("typ")] + new_typ + token[match.end("typ") :])
    return variants


def add_trailing_isoform(token: str) -> str | None:
    if token.endswith("_") and "_1_" not in token.split("__")[-1]:
        candidate = token[:-1] + "_1_"
        if candidate != token:
            return candidate
    return None


def phosphorylate_receptors(token: str) -> str:
    """Old heterodimers often listed phospho sites on only one receptor."""
    return RECEPTOR_COMPONENT_RE.sub(r"p_\g<rec>", token)


def compartment_variants(token: str) -> list[str]:
    variants: list[str] = []
    if token.startswith("cyt_"):
        variants.append("nuc_" + token[4:])
    elif token.startswith("nuc_"):
        variants.append("cyt_" + token[4:])
    return variants


def strip_state(token: str) -> str | None:
    stripped = re.sub(
        r"^((?:cyt|nuc|mit|exc)_(?:cong|prot|mixed|comp|abs|mrna|gene))_(?:in|a|i)__",
        r"\1__",
        token,
        count=1,
    )
    return stripped if stripped != token else None


def expand_candidates(token: str) -> list[str]:
    bases = [token, *type_variants(token), *compartment_variants(token)]
    stripped = strip_state(token)
    if stripped:
        bases.append(stripped)
        bases.extend(type_variants(stripped))
        bases.extend(compartment_variants(stripped))
    candidates: list[str] = []
    for base in bases:
        candidates.append(base)
        candidates.extend(type_variants(base))
        iso = add_trailing_isoform(base)
        if iso:
            candidates.append(iso)
            candidates.extend(type_variants(iso))
            candidates.extend(compartment_variants(iso))
        for swapped in compartment_variants(base):
            candidates.append(swapped)
            candidates.extend(type_variants(swapped))
    return candidates


def map_token(token: str, species: set[str]) -> str | None:
    if token in species:
        return token
    rewritten = rewrite_token(token)
    phosphorylated = phosphorylate_receptors(rewritten)
    candidates: list[str] = []
    for base in (rewritten, phosphorylated):
        candidates.extend(expand_candidates(base))
    seen: set[str] = set()
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        if candidate in species:
            return candidate
    return None


def split_terms(formula: str) -> list[tuple[str, str | None]]:
    terms: list[tuple[str, str | None]] = []
    for raw in formula.split(" + "):
        raw = raw.strip()
        if not raw:
            continue
        match = TERM_RE.fullmatch(raw)
        if not match:
            raise ValueError(f"Unparseable formula term: {raw!r}")
        terms.append((match.group("id"), match.group("coef")))
    return terms


def join_terms(terms: list[tuple[str, str | None]]) -> str:
    parts: list[str] = []
    for species_id, coef in terms:
        if coef is None:
            parts.append(species_id)
        else:
            parts.append(f"{species_id} * {coef}")
    return " + ".join(parts)


def remap_formula(
    formula: str, species: set[str]
) -> tuple[str, int, int, int]:
    mapped: list[tuple[str, str | None]] = []
    n_kept = n_rewritten = n_dropped = 0
    used: set[str] = set()
    for token, coef in split_terms(formula):
        new_id = map_token(token, species)
        if new_id is None:
            n_dropped += 1
            continue
        if new_id == token:
            n_kept += 1
        else:
            n_rewritten += 1
        if new_id in used:
            continue
        used.add(new_id)
        mapped.append((new_id, coef))
    if not mapped:
        return "", n_kept, n_rewritten, n_dropped
    return join_terms(mapped), n_kept, n_rewritten, n_dropped


def load_head_observables() -> tuple[list[str], list[dict[str, str]]]:
    """Original SPARCED formulas live in git HEAD; local file may already be remapped."""
    rel = OBS_PATH.relative_to(REPO).as_posix()
    raw = subprocess.check_output(
        ["git", "show", f"HEAD:{rel}"],
        cwd=REPO,
        text=True,
        encoding="utf-8",
    )
    reader = csv.DictReader(io.StringIO(raw), delimiter="\t")
    fieldnames = list(reader.fieldnames or [])
    rows = [row for row in reader if row["observableId"] != "blank"]
    return fieldnames, rows


def main() -> None:
    species = load_species()
    fieldnames, rows = load_head_observables()

    original_end = next(
        i for i, row in enumerate(rows) if row["observableId"] == NEW_OBS_START
    )
    print(f"Remapping {original_end} original observables; leaving {len(rows) - original_end} new ones")

    empty_after = []
    still_stale = []
    changed = 0
    total_rewritten = total_dropped = 0
    for row in rows[:original_end]:
        new_formula, n_kept, n_rewritten, n_dropped = remap_formula(
            row["observableFormula"], species
        )
        total_rewritten += n_rewritten
        total_dropped += n_dropped
        tokens = TOKEN_RE.findall(new_formula) if new_formula else []
        missing = [t for t in tokens if t not in species]
        if not new_formula:
            empty_after.append(row["observableId"])
        if missing:
            still_stale.append((row["observableId"], missing))
        if new_formula != row["observableFormula"]:
            changed += 1
            row["observableFormula"] = new_formula

    print(f"  formulas changed: {changed}")
    print(f"  terms rewritten: {total_rewritten}")
    print(f"  terms dropped (no v1.2 ID): {total_dropped}")
    print(f"  empty after remap: {empty_after}")
    print(f"  still containing unknown tokens: {len(still_stale)}")
    for oid, missing in still_stale:
        print(f"    {oid}: {missing[:8]}{'...' if len(missing) > 8 else ''}")

    all_ok = not empty_after and not still_stale
    if not all_ok:
        raise SystemExit("Refusing to write: some original formulas are empty or still stale")

    with OBS_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=fieldnames, delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {OBS_PATH}")


if __name__ == "__main__":
    main()
