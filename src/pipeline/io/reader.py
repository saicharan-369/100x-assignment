"""Dataset readers handling the relaxed JSON format."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

import yaml

from src.utils.cleaning import ensure_sequence


class RawDatasetReader:
    """Load the raw property dataset into memory using YAML parser."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> list[dict[str, object]]:
        return ensure_sequence(yaml.safe_load(self.path.read_text(encoding="utf-8")))

    def stream(self) -> Iterable[dict[str, object]]:
        for record in ensure_sequence(yaml.safe_load(self.path.read_text(encoding="utf-8"))):
            yield record
