#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import defaultdict
from pathlib import Path

from config.in_house_file_format import EXTENSION as IN_HOUSE_EXTENSION
from config.in_house_file_format import InHouseFilesNames
from config.settings import INPUT_DIR_NAME

from utils.path_validator import PathValidator


class InputScanner:
    def __init__(self, root_path: str | Path):
        # Resolve paths
        self.root_path = PathValidator.directory(root_path)
        self.data_path = PathValidator.directory(self.root_path / Path(INPUT_DIR_NAME.lstrip("/\\")))
        # Create data structures
        self.in_house_files = {file_type: [] for file_type in InHouseFilesNames}
        self.remaining_files = defaultdict(list)
        # Store input files paths
        self._list_input_files()

    def __repr__(self):
        return f"Model path: {self.root_path}"

    def _add_in_house_file(self, file_path: str | Path):
        file_name = InHouseFilesNames(Path(file_path).stem)
        self.in_house_files[file_name].append(file_path)

    def _list_input_files(self):
        for file_path in self.data_path.rglob("*"):
            if not file_path.is_file(): # Don't list directories, just files
                continue
            if file_path.suffix == IN_HOUSE_EXTENSION:
                self._add_in_house_file(file_path)
            else:
                extension = file_path.suffix.lower()
                self.remaining_files[extension].append(file_path)

