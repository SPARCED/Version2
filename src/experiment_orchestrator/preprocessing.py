#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path

import yaml

from config.paths import PROTOCOLS_DIR_PATH


def load_config(protocol_relative_path: str | Path, model_relative_path: str | Path):
    # Resolve paths
    protocol_path = PROTOCOLS_DIR_PATH / Path(protocol_relative_path.lstrip("/\\"))

    if not protocol_path.exists():
        raise ValueError(f"Invalid path")
    if not protocol_path.is_file():
        raise ValueError(f"Given path is not a file")

    # Read configuration
    with open(protocol_path) as f:
        config = yaml.safe_load(f)

    # VALIDATE the config before sending it to all cores!!
    # required = ["sbml_file", "output_dir"]
    # for key in required:
    #   if key not in config:
    #       raise ValueError(f"Missing configuration key: {key}.")

    return config

