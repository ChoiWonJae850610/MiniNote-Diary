from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from services.inbound.repository import InboundRepository
from services.order.repository import OrderRepository
from services.product.repository import ProductRepository
from services.work_order.repository import WorkOrderRepository


@dataclass(frozen=True)
class DashboardMetric:
    label: str
    value: str


@dataclass(frozen=True)
class DashboardListItem:
    primary: str
    secondary: str
    tertiary: str = ''


@dataclass(frozen=True)
class DashboardData:
    metrics: tuple[DashboardMetric, ...]
    recent_templates: tuple[DashboardListItem, ...]
    recent_activity: tuple[DashboardListItem, ...]


class DashboardService:
    def __init__(self, base_dir: str | Path):
        self.base_dir = Path(base_dir)
        self.work_order_repository = WorkOrderRepository(self.base_dir)
        self.order_repository = OrderRepository(self.base_dir)
        self.inbound_repository = InboundRepository(self.base_dir)
        self.product_repository = ProductRepository(self.base_dir)

    def build_dashboard(self) -> DashboardData:
        template_summaries = self.work_order_repository.list_template_summaries()
        orders = self.order_repository.load_all()
        inbound_records = self.inbound_repository.load_all()
        product_rows = self.product_repository.load_all()

        total_templates = len(template_summaries)
        in_progress_orders = sum(1 for row in orders if max(0, int(row.ordered_qty or 0)) > max(0, int(row.completed_qty or 0)))
        pending_inspections = sum(1 for row in inbound_records if (row.inspection_status or 'completed') == 'pending')

        completed_good_qty = sum(max(0, int(row.good_qty or 0)) for row in inbound_records if (row.inspection_status or 'completed') != 'pending')
        sold_qty = sum(max(0, int(row.sold_qty or 0)) for row in orders)
        current_stock_qty = max(0, completed_good_qty - sold_qty)

        metrics = (
            DashboardMetric('총 작업지시서', str(total_templates)),
            DashboardMetric('진행중 발주', str(in_progress_orders)),
            DashboardMetric('미검수 건수', str(pending_inspections)),
            DashboardMetric('현재고 합계', str(current_stock_qty)),
        )

        recent_templates = tuple(
            DashboardListItem(
                primary=summary.name or summary.template_id,
                secondary=' · '.join(part for part in (summary.date or '', summary.factory_name or '거래처 없음') if part) or '기본 정보 없음',
                tertiary=(summary.change_note or '').strip() or f'원단 {summary.fabric_count} / 부자재 {summary.trim_count}',
            )
            for summary in template_summaries[:5]
        )

        activity_rows: list[tuple[str, str, str, str]] = []
        for row in orders:
            activity_rows.append((
                row.created_at or row.ordered_at or '',
                '발주',
                row.template_name or row.template_id,
                f'{row.ordered_at or "날짜 없음"} · {max(0, int(row.ordered_qty or 0))}개',
            ))
        for row in inbound_records:
            activity_rows.append((
                row.created_at or row.inbound_date or '',
                '입고',
                row.template_name or row.template_id,
                f'{row.inbound_date or "날짜 없음"} · 양품 {max(0, int(row.good_qty or 0))} / 불량 {max(0, int(row.defect_qty or 0))}',
            ))
        for row in product_rows:
            activity_rows.append((
                row.updated_at or '',
                '상품',
                row.template_name or row.template_id,
                f'판매가 {max(0, int(row.sale_price or 0)):,}원',
            ))

        activity_rows.sort(key=lambda item: item[0], reverse=True)
        recent_activity = tuple(
            DashboardListItem(
                primary=f'[{kind}] {name}',
                secondary=detail,
                tertiary=(timestamp or '')[:10],
            )
            for timestamp, kind, name, detail in activity_rows[:5]
        )

        return DashboardData(metrics=metrics, recent_templates=recent_templates, recent_activity=recent_activity)
