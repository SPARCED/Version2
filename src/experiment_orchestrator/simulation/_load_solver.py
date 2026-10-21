#!/usr/bin/env python
# -*- coding: utf-8 -*-

# From Benchtop's registry.py (9a12e65)
# Written by Jonah R. Huggins
# Adapted by Aurore K. Amrit

import importlib

from config.solvers import SOLVERS_REGISTRY


def load_solver(name: str):
    """Import and return a simulator class by registry name."""
    if name not in SOLVERS_REGISTRY:
        raise KeyError(name)
    import_path = SOLVERS_REGISTRY[name]
    module_path, class_name = import_path.rsplit(".", 1)

    try:
        module = importlib.import_module(module_path)
    except ModuleNotFoundError as e:
        raise ImportError(
                f"The simulator '{name}' requires optional dependencies."
                ) from e
    return getattr(module, class_name)

