from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import importlib

MODULES = [
    "services.common.project_paths",
    "services.partner.repository",
    "services.unit.repository",
    "services.order.repository",
    "services.work_order.repository",
    "services.work_order.service",
    "ui.postit",
    "ui.postit.layout",
    "ui.postit.stack",
]


def main() -> int:
    failed: list[str] = []
    for module_name in MODULES:
        try:
            importlib.import_module(module_name)
            print(f"ok: {module_name}")
        except ModuleNotFoundError as exc:
            if exc.name == "PySide6":
                print(f"skip: {module_name} (PySide6 unavailable)")
                continue
            failed.append(f"{module_name}: {exc}")
        except Exception as exc:
            failed.append(f"{module_name}: {exc}")
    if failed:
        print("import smoke test failed")
        for row in failed:
            print(row)
        return 1
    print("import smoke test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
