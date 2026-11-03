#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path


class PathValidator:
    @staticmethod
    def directory(path: str | Path) -> Path:
        p = Path(path).resolve()

        if not p.exists():
            raise FileNotFoundError(f"{path}")
        if not p.is_dir():
            raise NotADirectoryError(f"{path}")

        return p

    @staticmethod
    def file(path: str | Path, expected_suffix: str | None = None) -> Path:
        p = Path(path).resolve()

        if not p.exists():
            raise FileNotFoundError(f"{path}")
        if not p.is_file():
            raise FileNotFoundError(f"{path}")

        if expected_suffix is not None and p.suffix.lower() != expected_suffix.lower():
            raise ValueError(f"Expected a {expected_suffix} file ; got: {path}")

        return p

