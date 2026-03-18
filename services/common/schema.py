from __future__ import annotations

from typing import Iterable

from services.common.field_keys import DbFilenames, HeaderKeys, MaterialKeys

HEADER_FIELDS: tuple[str, ...] = (
    HeaderKeys.DATE,
    HeaderKeys.STYLE_NO,
    HeaderKeys.FACTORY,
    HeaderKeys.PRODUCT_TYPE,
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
    HeaderKeys.PRODUCT_TYPE,
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

MAX_MATERIAL_ITEMS = 10


def make_empty_mapping(fields: Iterable[str]) -> dict[str, str]:
    return {field: '' for field in fields}


PARTNERS_DB_FILENAME = DbFilenames.PARTNERS
PARTNER_TYPES_DB_FILENAME = DbFilenames.PARTNER_TYPES
PRODUCT_TYPES_DB_FILENAME = DbFilenames.PRODUCT_TYPES
ORDER_RUNS_DB_FILENAME = DbFilenames.ORDER_RUNS
