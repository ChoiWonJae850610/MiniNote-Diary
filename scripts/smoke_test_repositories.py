from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from services.order.repository import OrderRepository
from services.partner.repository import PartnerRepository
from services.unit.repository import UnitRepository
from services.work_order.repository import WorkOrderRepository


def main() -> int:
    partners = PartnerRepository().load_all()
    partner_types = PartnerRepository().load_types()
    units = UnitRepository().load_all()
    orders = OrderRepository().load_all()
    work_orders = WorkOrderRepository().list_templates()

    print(f"partners={len(partners)}")
    print(f"partner_types={len(partner_types)}")
    print(f"units={len(units)}")
    print(f"orders={len(orders)}")
    print(f"work_orders={len(work_orders)}")
    print("repository smoke test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
