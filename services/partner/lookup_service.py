from __future__ import annotations

from services.partner.repository import PartnerRecord, PartnerRepository
from services.partner.utils import (
    PARTNER_TYPE_DYEING,
    PARTNER_TYPE_FACTORY,
    PARTNER_TYPE_FABRIC,
    PARTNER_TYPE_FINISH,
    PARTNER_TYPE_OTHER,
    PARTNER_TYPE_TRIM,
)


class PartnerLookupService:
    _TYPE_ALIASES = {
        PARTNER_TYPE_FACTORY: {PARTNER_TYPE_FACTORY},
        PARTNER_TYPE_FABRIC: {PARTNER_TYPE_FABRIC},
        PARTNER_TYPE_TRIM: {PARTNER_TYPE_TRIM},
        PARTNER_TYPE_DYEING: {PARTNER_TYPE_DYEING, "나염"},
        PARTNER_TYPE_FINISH: {PARTNER_TYPE_FINISH},
    }

    def __init__(self, project_root: str):
        self.project_root = project_root
        self.repository = PartnerRepository(project_root)

    def partners_for_type(self, partner_type: str) -> list[PartnerRecord]:
        partner_type = str(partner_type or '').strip()
        rows = self.repository.load_partners()
        if partner_type == PARTNER_TYPE_OTHER:
            excluded = set().union(*self._TYPE_ALIASES.values())
            return [
                row
                for row in rows
                if any(partner_type_name not in excluded for partner_type_name in (row.types or []))
                or PARTNER_TYPE_OTHER in (row.types or [])
            ]
        allowed = self._TYPE_ALIASES.get(partner_type, {partner_type})
        return [row for row in rows if any(type_name in allowed for type_name in (row.types or []))]
