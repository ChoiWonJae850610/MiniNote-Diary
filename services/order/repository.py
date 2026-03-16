from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from services.common.field_keys import PayloadKeys
from services.common.project_paths import db_file_path, project_root_path
from services.common.schema import ORDER_RUNS_DB_FILENAME


@dataclass
class OrderRecord:
    order_id: str
    template_id: str
    template_name: str
    factory_name: str
    ordered_qty: int
    ordered_at: str
    memo: str = ''
    status: str = 'ordered'
    completed_qty: int = 0
    sold_qty: int = 0
    created_at: str = ''


@dataclass
class TemplateOrderStats:
    template_id: str
    order_count: int = 0
    total_ordered_qty: int = 0
    in_progress_qty: int = 0
    completed_qty: int = 0
    sold_qty: int = 0
    current_stock_qty: int = 0
    last_ordered_at: str = ''


class OrderRepository:
    def __init__(self, base_dir: str | Path | None = None):
        self.base_dir = Path(base_dir) if base_dir is not None else project_root_path(__file__)

    @property
    def file_path(self) -> Path:
        return db_file_path(ORDER_RUNS_DB_FILENAME, self.base_dir)

    def load_all(self) -> list[OrderRecord]:
        payload = self._read_payload()
        rows = payload.get(PayloadKeys.ORDERS, [])
        result: list[OrderRecord] = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            try:
                result.append(OrderRecord(**row))
            except TypeError:
                continue
        return result

    def save_all(self, orders: list[OrderRecord]) -> None:
        payload = self._read_payload()
        payload[PayloadKeys.ORDERS] = [asdict(order) for order in orders]
        payload[PayloadKeys.UPDATED_AT] = datetime.now().isoformat(timespec='seconds')
        self._write_payload(payload)

    def list_orders(self) -> list[OrderRecord]:
        return self.load_all()

    def create_order(self, *, template_id: str, template_name: str, factory_name: str, ordered_qty: int, ordered_at: str, memo: str = '') -> OrderRecord:
        now = datetime.now().isoformat(timespec='seconds')
        order = OrderRecord(
            order_id=f'order_{int(datetime.now().timestamp() * 1000)}',
            template_id=template_id,
            template_name=template_name,
            factory_name=factory_name,
            ordered_qty=max(1, int(ordered_qty)),
            ordered_at=ordered_at,
            memo=(memo or '').strip(),
            created_at=now,
        )
        orders = self.load_all()
        orders.append(order)
        self.save_all(orders)
        return order

    def aggregate_by_template(self) -> dict[str, TemplateOrderStats]:
        grouped: dict[str, TemplateOrderStats] = {}
        for order in self.load_all():
            stats = grouped.setdefault(order.template_id, TemplateOrderStats(template_id=order.template_id))
            stats.order_count += 1
            stats.total_ordered_qty += max(0, int(order.ordered_qty or 0))
            stats.completed_qty += max(0, int(order.completed_qty or 0))
            stats.sold_qty += max(0, int(order.sold_qty or 0))
            if order.status in {'ordered', 'in_progress'}:
                stats.in_progress_qty += max(0, int(order.ordered_qty or 0))
            if order.ordered_at and (not stats.last_ordered_at or order.ordered_at > stats.last_ordered_at):
                stats.last_ordered_at = order.ordered_at
        for stats in grouped.values():
            stats.current_stock_qty = max(0, stats.completed_qty - stats.sold_qty)
        return grouped

    def aggregate_for_template(self, template_id: str) -> TemplateOrderStats:
        return self.aggregate_by_template().get(template_id, TemplateOrderStats(template_id=template_id))

    def _read_payload(self) -> dict[str, Any]:
        path = self.file_path
        if not path.is_file():
            return {PayloadKeys.VERSION: 1, PayloadKeys.ORDERS: []}
        try:
            payload = json.loads(path.read_text(encoding='utf-8'))
        except Exception:
            return {PayloadKeys.VERSION: 1, PayloadKeys.ORDERS: []}
        if not isinstance(payload, dict):
            return {PayloadKeys.VERSION: 1, PayloadKeys.ORDERS: []}
        if not isinstance(payload.get(PayloadKeys.ORDERS), list):
            payload[PayloadKeys.ORDERS] = []
        return payload

    def _write_payload(self, payload: dict[str, Any]) -> None:
        path = self.file_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
