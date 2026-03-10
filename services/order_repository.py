from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from services.schema import ORDER_RUNS_DB_FILENAME
from services.storage import ensure_db_dir


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
    def __init__(self, base_dir: str | Path):
        self.base_dir = str(base_dir)

    def list_orders(self) -> list[OrderRecord]:
        payload = self._read_payload()
        rows = payload.get('orders', [])
        result: list[OrderRecord] = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            try:
                result.append(OrderRecord(**row))
            except TypeError:
                continue
        return result

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
        payload = self._read_payload()
        rows = payload.setdefault('orders', [])
        rows.append(asdict(order))
        payload['updated_at'] = now
        self._write_payload(payload)
        return order

    def aggregate_by_template(self) -> dict[str, TemplateOrderStats]:
        grouped: dict[str, TemplateOrderStats] = {}
        for order in self.list_orders():
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

    def _db_path(self) -> str:
        return os.path.join(ensure_db_dir(self.base_dir), ORDER_RUNS_DB_FILENAME)

    def _read_payload(self) -> dict[str, Any]:
        path = self._db_path()
        if not os.path.isfile(path):
            return {'version': 1, 'orders': []}
        try:
            with open(path, 'r', encoding='utf-8') as f:
                payload = json.load(f)
        except Exception:
            return {'version': 1, 'orders': []}
        if not isinstance(payload, dict):
            return {'version': 1, 'orders': []}
        if not isinstance(payload.get('orders'), list):
            payload['orders'] = []
        return payload

    def _write_payload(self, payload: dict[str, Any]) -> None:
        path = self._db_path()
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
