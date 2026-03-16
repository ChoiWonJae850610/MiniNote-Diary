from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from services.common.project_paths import db_dir_path, project_root_path


def main() -> int:
    root = project_root_path(__file__)
    db_dir = db_dir_path(__file__)
    required = ["partners.json", "partner_types.json", "units.json", "job_orders.json"]
    missing = [name for name in required if not (db_dir / name).exists()]
    print(f"project_root={root}")
    print(f"db_dir={db_dir}")
    if missing:
        print("missing=" + ",".join(missing))
        return 1
    print("path smoke test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
