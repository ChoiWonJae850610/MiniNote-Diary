from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Iterable

from services.common.models import MaterialItem
from services.order.repository import TemplateOrderStats
from services.work_order.repository import WorkOrderTemplateDetail


@dataclass(frozen=True)
class MaterialLineSummary:
    partner: str
    item: str
    qty: str
    unit: str
    unit_price: str
    total: str
    total_amount: int


@dataclass(frozen=True)
class MaterialPartnerSummary:
    partner: str
    items: list[MaterialLineSummary]
    subtotal_amount: int


@dataclass(frozen=True)
class MaterialCategorySummary:
    key: str
    title: str
    partners: list[MaterialPartnerSummary]
    subtotal_amount: int
    item_count: int


@dataclass(frozen=True)
class WorkOrderSummaryView:
    name: str
    factory_name: str
    date: str
    change_note: str
    image_attached: bool
    categories: list[MaterialCategorySummary]
    total_amount: int
    order_stats: TemplateOrderStats | None = None

    @property
    def material_summary_text(self) -> str:
        counts = []
        for category in self.categories:
            counts.append(f"{category.title} {category.item_count}")
        return " / ".join(counts) if counts else "자재 없음"

    def to_detail_text(self) -> str:
        lines: list[str] = []
        if self.name:
            lines.append(f"작업지시서: {self.name}")
        if self.factory_name:
            lines.append(f"공장: {self.factory_name}")
        if self.date:
            lines.append(f"기준일: {self.date}")
        if self.order_stats is not None:
            last_order = self.order_stats.last_ordered_at or "없음"
            lines.append(f"발주이력: {self.order_stats.order_count}건 / 최근 {last_order}")
        lines.append("")
        for category in self.categories:
            lines.append(f"[{category.title}]")
            if not category.partners:
                lines.append("- 내역 없음")
                lines.append("")
                continue
            for partner_summary in category.partners:
                lines.append(partner_summary.partner)
                for item in partner_summary.items:
                    qty_text = f"{item.qty}{item.unit}".strip()
                    qty_text = qty_text or "-"
                    unit_price_text = item.unit_price or "-"
                    total_text = item.total or _format_amount(item.total_amount)
                    lines.append(f"  - {item.item or '-'} / {qty_text} / {unit_price_text} / {total_text}")
                lines.append(f"  소계: {_format_amount(partner_summary.subtotal_amount)}")
            lines.append(f"{category.title} 합계: {_format_amount(category.subtotal_amount)}")
            lines.append("")
        lines.append(f"총 재료비: {_format_amount(self.total_amount)}")
        if self.change_note:
            lines.append("")
            lines.append("메모")
            lines.append(self.change_note)
        return "\n".join(lines).strip()


_CATEGORY_SPECS = (
    ("fabrics", "원단"),
    ("trims", "부자재"),
    ("dyeings", "염색"),
    ("finishings", "마감"),
    ("others", "기타"),
)


def build_work_order_summary_view(
    detail: WorkOrderTemplateDetail,
    *,
    order_stats: TemplateOrderStats | None = None,
) -> WorkOrderSummaryView:
    categories: list[MaterialCategorySummary] = []
    total_amount = 0
    for attr_name, title in _CATEGORY_SPECS:
        category = _build_category_summary(attr_name, title, getattr(detail.document, attr_name, []))
        categories.append(category)
        total_amount += category.subtotal_amount
    return WorkOrderSummaryView(
        name=detail.summary.name,
        factory_name=detail.summary.factory_name,
        date=detail.summary.date,
        change_note=detail.summary.change_note,
        image_attached=bool(detail.summary.image_path),
        categories=categories,
        total_amount=total_amount,
        order_stats=order_stats,
    )


def _build_category_summary(key: str, title: str, items: Iterable[MaterialItem]) -> MaterialCategorySummary:
    grouped: dict[str, list[MaterialLineSummary]] = {}
    item_count = 0
    for item in items or []:
        if not item.has_any_value():
            continue
        item_count += 1
        total_amount = _to_amount(item.total)
        line = MaterialLineSummary(
            partner=(item.vendor or "거래처 미지정").strip() or "거래처 미지정",
            item=(item.item or "").strip(),
            qty=(item.qty or "").strip(),
            unit=(item.unit or "").strip(),
            unit_price=(item.unit_price or "").strip(),
            total=(item.total or "").strip(),
            total_amount=total_amount,
        )
        grouped.setdefault(line.partner, []).append(line)
    partners: list[MaterialPartnerSummary] = []
    subtotal_amount = 0
    for partner_name in sorted(grouped.keys()):
        lines = grouped[partner_name]
        partner_total = sum(line.total_amount for line in lines)
        subtotal_amount += partner_total
        partners.append(MaterialPartnerSummary(partner=partner_name, items=lines, subtotal_amount=partner_total))
    return MaterialCategorySummary(
        key=key,
        title=title,
        partners=partners,
        subtotal_amount=subtotal_amount,
        item_count=item_count,
    )


def _to_amount(value: str) -> int:
    text = (value or "").strip().replace(",", "")
    if not text:
        return 0
    try:
        return int(Decimal(text))
    except (InvalidOperation, ValueError):
        return 0


def _format_amount(value: int) -> str:
    return f"{int(value):,}"


__all__ = [
    "WorkOrderSummaryView",
    "build_work_order_summary_view",
]
