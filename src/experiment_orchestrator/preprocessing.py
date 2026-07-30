#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path

import yaml

from config.paths import PROTOCOLS_DIR_PATH
from config.protocol_file_format import PROTOCOL_REQUIRED_KEYS


def load_context(protocol_relative_path: str | Path, model_relative_path: str | Path):
    # Resolve paths
    protocol_path = PROTOCOLS_DIR_PATH / Path(protocol_relative_path.lstrip("/\\"))

    if not protocol_path.exists():
        raise ValueError(f"Invalid path")
    if not protocol_path.is_file():
        raise ValueError(f"Given path is not a file")

    # Read context
    with open(protocol_path) as f:
        context = yaml.safe_load(f)

    # Validate the context before sending it to all cores!! 
    if not isinstance(context, dict):
        raise ValueError("Protocol should be a YAML dictionnary.")
    missing = [key for key in PROTOCOL_REQUIRED_KEYS if key not in context]
    if missing:
        raise ValueError(f"Missing key(s) in protocol: {', '.join(missing)}")

    return context

