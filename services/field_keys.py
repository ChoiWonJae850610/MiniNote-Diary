from __future__ import annotations


class HeaderKeys:
    DATE = "date"
    STYLE_NO = "style_no"
    FACTORY = "factory"
    COST_DISPLAY = "cost_display"
    LABOR_DISPLAY = "labor_display"
    LOSS_DISPLAY = "loss_display"
    SALE_PRICE_DISPLAY = "sale_price_display"
    COST = "cost"
    LABOR = "labor"
    LOSS = "loss"
    SALE_PRICE = "sale_price"
    CHANGE_NOTE = "change_note"


class MaterialKeys:
    VENDOR = "거래처"
    VENDOR_ID = "거래처_id"
    LEGACY_FABRIC_VENDOR = "원단처"
    ITEM = "품목"
    QTY = "수량"
    UNIT = "단위"
    UNIT_PRICE = "단가"
    TOTAL = "총액"


class MaterialTargets:
    FABRIC = "fabric"
    TRIM = "trim"
    DYEING = "dyeing"
    FINISHING = "finishing"
    OTHER = "other"

    ALL: tuple[str, ...] = (FABRIC, TRIM, DYEING, FINISHING, OTHER)


class PayloadKeys:
    VERSION = "version"
    UPDATED_AT = "updated_at"
    SAVED_AT = "saved_at"
    HEADER = "header"
    FABRICS = "fabrics"
    TRIMS = "trims"
    DYEINGS = "dyeings"
    FINISHINGS = "finishings"
    OTHERS = "others"
    IMAGE_ATTACHED = "image_attached"
    ORDERS = "orders"


class DbFilenames:
    PARTNERS = "partners.json"
    PARTNER_TYPES = "partner_types.json"
    UNITS = "units.json"
    ORDER_RUNS = "job_orders.json"
