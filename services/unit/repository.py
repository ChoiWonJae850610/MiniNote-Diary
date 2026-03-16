from __future__ import annotations

import json
from pathlib import Path
from typing import List, Tuple


UnitOption = Tuple[str, str]


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def unit_file_path(base_dir: str | Path | None = None) -> Path:
    base = Path(base_dir) if base_dir is not None else _repo_root()
    return base / "db" / "units.json"


def load_units(base_dir: str | Path | None = None) -> List[UnitOption]:
    path = unit_file_path(base_dir)
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        return []

    if isinstance(data, dict):
        units = data.get("units", [])
    elif isinstance(data, list):
        units = data
    else:
        units = []

    out: List[UnitOption] = []
    for item in units if isinstance(units, list) else []:
        if not isinstance(item, dict):
            continue
        unit = str(item.get("unit", "") or "").strip()
        label = str(item.get("label", "") or "").strip()
        if unit or label:
            out.append((unit, label or unit))
    return out


def unit_label_for_value(unit: str, options: List[UnitOption] | None = None) -> str:
    current = str(unit or "").strip()
    for value, label in options or []:
        if value == current:
            return label
    return current



def save_units(options: list[UnitOption], base_dir: str | Path | None = None) -> None:
    path = unit_file_path(base_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for value, label in options:
        unit = str(value or "").strip()
        display = str(label or "").strip()
        if not unit and not display:
            continue
        rows.append({"unit": unit, "label": display or unit})
    path.write_text(json.dumps({"units": rows}, ensure_ascii=False, indent=2), encoding="utf-8")
