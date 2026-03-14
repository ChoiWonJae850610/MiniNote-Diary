from __future__ import annotations

from typing import Iterable

from services.unit_repository import UnitOption, load_units, save_units


class UnitService:
    def __init__(self, project_root: str):
        self.project_root = project_root

    def list_units(self) -> list[dict[str, str]]:
        return [
            {"unit": value, "label": label}
            for value, label in load_units(self.project_root)
        ]

    def save_units(self, units: Iterable[dict[str, str]]) -> None:
        cleaned: list[UnitOption] = []
        for row in units:
            if not isinstance(row, dict):
                continue
            unit = str(row.get("unit", "") or "").strip()
            label = str(row.get("label", "") or "").strip()
            if not unit and not label:
                continue
            cleaned.append((unit, label or unit))
        save_units(cleaned, self.project_root)
