#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path

import yaml

from config.paths import PROTOCOLS_DIR_PATH

from utils.context_validation import validate_context


def load_context(protocol_relative_path: str | Path):
    # Resolve paths
    protocol_path = PROTOCOLS_DIR_PATH / Path(protocol_relative_path.lstrip("/\\"))

    if not protocol_path.exists():
        raise ValueError(f"Invalid protocol path")
    if not protocol_path.is_file():
        raise ValueError(f"Given protocol path is not a file")

    # Read context
    with open(protocol_path) as f:
        context = yaml.safe_load(f)

    # Validate the context before sending it to all cores!!
    validate_context(context)

    return context

