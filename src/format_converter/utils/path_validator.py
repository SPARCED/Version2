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

