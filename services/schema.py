from __future__ import annotations

from typing import Iterable

from services.field_keys import HeaderKeys, MaterialKeys
from ui.messages import Tooltips

HEADER_FIELDS: tuple[str, ...] = (
    HeaderKeys.DATE,
    HeaderKeys.STYLE_NO,
    HeaderKeys.FACTORY,
    HeaderKeys.COST_DISPLAY,
    HeaderKeys.LABOR_DISPLAY,
    HeaderKeys.LOSS_DISPLAY,
    HeaderKeys.SALE_PRICE_DISPLAY,
    HeaderKeys.COST,
    HeaderKeys.LABOR,
    HeaderKeys.LOSS,
    HeaderKeys.SALE_PRICE,
    HeaderKeys.CHANGE_NOTE,
)

REQUIRED_HEADER_FIELDS: tuple[str, ...] = (
    HeaderKeys.DATE,
    HeaderKeys.STYLE_NO,
    HeaderKeys.FACTORY,
    HeaderKeys.COST_DISPLAY,
    HeaderKeys.LABOR_DISPLAY,
    HeaderKeys.LOSS_DISPLAY,
    HeaderKeys.SALE_PRICE_DISPLAY,
)

MATERIAL_FIELDS: tuple[str, ...] = (
    MaterialKeys.VENDOR,
    MaterialKeys.ITEM,
    MaterialKeys.QTY,
    MaterialKeys.UNIT,
    MaterialKeys.UNIT_PRICE,
    MaterialKeys.TOTAL,
)

REQUIRED_MATERIAL_FIELDS: tuple[str, ...] = (
    MaterialKeys.VENDOR,
    MaterialKeys.ITEM,
    MaterialKeys.QTY,
    MaterialKeys.UNIT_PRICE,
    MaterialKeys.TOTAL,
)

MAX_MATERIAL_ITEMS = 15
SUPPORTED_IMAGE_FILTER = 'Images (*.png *.jpg *.jpeg *.bmp)'
DEFAULT_FEEDBACK_TIMEOUT_MS = 2200


def make_empty_mapping(fields: Iterable[str]) -> dict[str, str]:
    return {field: '' for field in fields}


PARTNERS_DB_FILENAME = 'partners.json'
PARTNER_TYPES_DB_FILENAME = 'partner_types.json'
PARTNER_PICKER_TOOLTIP = Tooltips.PARTNER_MANAGE
ORDER_RUNS_DB_FILENAME = 'job_orders.json'
ORDER_PAGE_ALL_MONTHS_LABEL = '전체 월'
