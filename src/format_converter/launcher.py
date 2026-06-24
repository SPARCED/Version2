#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path

from config.paths import MODELS_DIR_PATH

from utils.path_validator import PathValidator

from data_storage import DataStorage
from input_scanner import InputScanner
from sbml_exporter import SBMLExporter


def convert_model(relative_path: str | Path):
    # Retrieve input files paths
    root = PathValidator.directory(MODELS_DIR_PATH / Path(relative_path.lstrip("/\\")))
    input_files = InputScanner(root)
    # Load input data
    model_data = DataStorage()
    model_data.load_in_house_files(input_files.in_house_files)
    # Convert the model
    exporter = SBMLExporter(root)
    exporter.to_sbml(model_data)

if __name__ == "__main__":
    convert_model("/official/2027")

