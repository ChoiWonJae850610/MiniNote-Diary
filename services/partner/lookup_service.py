from __future__ import annotations

from services.partner.repository import PartnerRecord, PartnerRepository
from services.partner.utils import (
    PARTNER_TYPE_FACTORY,
    PARTNER_TYPE_FABRIC,
    PARTNER_TYPE_OTHER,
    PARTNER_TYPE_TRIM,
)


class PartnerLookupService:
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.repository = PartnerRepository(project_root)

    def partners_for_type(self, partner_type: str) -> list[PartnerRecord]:
        if partner_type == PARTNER_TYPE_OTHER:
            excluded = {PARTNER_TYPE_FACTORY, PARTNER_TYPE_FABRIC, PARTNER_TYPE_TRIM}
            return [
                row
                for row in self.repository.load_partners()
                if not any(partner_type_name in excluded for partner_type_name in (row.types or []))
            ]
        return self.repository.load_partners_by_type(partner_type)
