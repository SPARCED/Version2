#!/usr/bin/env python3
"""RPPA paired heatmap: HECM (left) vs experimental RPPA (right).

Uses only Benchtop pickle data via ``notebooks/lincs_paired_heatmap.py``.

    python benchmarks/LINCS-RPPA-Abundance/plot_rppa_heatmaps.py
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / "notebooks"))

from lincs_paired_heatmap import main  # noqa: E402

if __name__ == "__main__":
    args = [
        "--pkl",
        str(HERE / "LINCS-RPPA-Abundance.pkl"),
        "--output",
        str(HERE / "figures" / "HECM-vs-RPPA-heatmap.png"),
        "--sim-title",
        "HECM",
        "--exp-title",
        "RPPA",
    ]
    main(args + sys.argv[1:])
